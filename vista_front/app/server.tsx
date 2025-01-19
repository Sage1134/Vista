import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { MongoClient } from 'mongodb';
import dotenv from 'dotenv';
import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';

dotenv.config({ path: 'vars.env' });

const uri = process.env.MONGODB_URI || '';
const ip = process.env.BackendIP || 'localhost';
const port = Number(process.env.Port) || 3000;

// MongoDB
const mongoClient = new MongoClient(uri);
let collection: any;

async function initDB() {
  await mongoClient.connect();
  const database = mongoClient.db('Vista');
  collection = database.collection('VistaCluster');
}
initDB().catch(console.error);

// In-memory data structures
const sessionTokens: Record<string, string> = {};
const USER_STATE = new Map<any, any>();
let WAITING_QUEUE: any[] = [];

// Helper to set session token with 24h expiration
function addSessionToken(username: string, token: string) {
  sessionTokens[username] = token;
  setTimeout(() => {
    if (sessionTokens[username] === token) {
      delete sessionTokens[username];
    }
  }, 86400000);
}

// Example DB getData
async function getData(path: string[]) {
  const dataCursor = collection.find({});
  const docs = await dataCursor.toArray();
  const firstLevelKey = path[0];
  let foundDoc = docs.find((doc: any) => doc._id === firstLevelKey);
  if (!foundDoc) return null;

  // Walk deeper keys
  for (let i = 1; i < path.length; i++) {
    if (!(path[i] in foundDoc)) return null;
    foundDoc = foundDoc[path[i]];
  }
  return foundDoc;
}

// Example DB setData
async function setData(path: string[], value: any) {
  const firstLevelKey = path[0];
  let doc = await collection.findOne({ _id: firstLevelKey });
  if (!doc) {
    doc = { _id: firstLevelKey };
  }
  let pointer = doc;
  for (let i = 1; i < path.length - 1; i++) {
    const key = path[i];
    if (!(key in pointer)) pointer[key] = {};
    pointer = pointer[key];
  }
  pointer[path[path.length - 1]] = value;
  await collection.findOneAndReplace({ _id: firstLevelKey }, doc, { upsert: true });
}

// Match two clients
async function matchTwoClients(clientA: any, clientB: any) {
  USER_STATE.get(clientA).status = 'matched';
  USER_STATE.get(clientB).status = 'matched';

  clientA.emit('matchFound', {
    question: USER_STATE.get(clientB).question,
  });
  clientB.emit('matchFound', {
    question: USER_STATE.get(clientA).question,
  });

  USER_STATE.get(clientA).partner = clientB;
  USER_STATE.get(clientB).partner = clientA;
}

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, { cors: { origin: '*' } });

io.on('connection', (socket) => {
  // Initialize user state
  USER_STATE.set(socket, {
    status: 'idle',
    question: null,
    answer: null,
    partner: null,
  });

  socket.on('register', async (msg) => {
    const { username, password } = msg;
    const existing = await getData(['Credentials', username]);
    if (!existing) {
      const hashed = crypto.createHash('sha256').update(password).digest('hex');
      await setData(['Credentials', username, 'password'], hashed);
      socket.emit('registerSuccess', { result: 'Registration Successful!' });
    } else {
      socket.emit('usernameAlreadyTaken', { result: 'Username already taken.' });
    }
  });

  socket.on('signIn', async (msg) => {
    const { username, password } = msg;
    const hashed = crypto.createHash('sha256').update(password).digest('hex');
    const storedHash = await getData(['Credentials', username, 'password']);
    if (hashed === storedHash) {
      const sessionToken = uuidv4();
      addSessionToken(username, sessionToken);
      socket.emit('signInSuccess', { sessionToken });
    } else {
      socket.emit('fail', { reason: 'Invalid credentials.' });
    }
  });

  socket.on('signOut', (msg) => {
    const { username, sessionToken } = msg;
    if (sessionTokens[username] === sessionToken) {
      delete sessionTokens[username];
      socket.emit('signOutSuccess');
    } else {
      socket.emit('fail');
    }
  });

  socket.on('askQuestion', (msg) => {
    const state = USER_STATE.get(socket);
    if (state.status === 'idle') {
      state.question = msg.question;
      state.status = 'waiting';

      if (WAITING_QUEUE.length > 0) {
        const other = WAITING_QUEUE.shift();
        matchTwoClients(socket, other);
      } else {
        WAITING_QUEUE.push(socket);
        socket.emit('waiting');
      }
    } else {
      console.log('Client not idle, ignoring question.');
    }
  });

  socket.on('provideAnswer', (msg) => {
    const state = USER_STATE.get(socket);
    if (state.status === 'matched') {
      state.answer = msg.answer;
      const partner = state.partner;
      const partnerState = USER_STATE.get(partner);
      if (partner && partnerState.answer !== null) {
        const yourAnswer = state.answer;
        const partnerAnswer = partnerState.answer;
        socket.emit('answerReceived', { answer: partnerAnswer });
        partner.emit('answerReceived', { answer: yourAnswer });

        // reset
        state.status = 'idle';
        state.question = null;
        state.answer = null;
        state.partner = null;
        partnerState.status = 'idle';
        partnerState.question = null;
        partnerState.answer = null;
        partnerState.partner = null;
      }
    } else {
      console.log('Client not matched, ignoring answer.');
    }
  });

  socket.on('disconnect', () => {
    // Remove client from WAITING_QUEUE if present
    WAITING_QUEUE = WAITING_QUEUE.filter((c) => c !== socket);

    // Notify partner if matched
    const partner = USER_STATE.get(socket)?.partner;
    if (partner) {
      const partnerState = USER_STATE.get(partner);
      partnerState.partner = null;
      partnerState.answer = null;
      if (partnerState.status === 'matched') {
        partner.emit('partnerDisconnected');
        partnerState.status = 'idle';
      }
    }
    USER_STATE.delete(socket);
    console.log('Client disconnected:', socket.id);
  });
});

httpServer.listen(port, ip, () => {
  console.log(`Server running on http://${ip}:${port}/`);
});