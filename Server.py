from pymongo import MongoClient
from dotenv import load_dotenv
import asyncio
import json
import websockets
import hashlib
import uuid
import os

load_dotenv("vars.env")

uri = os.environ.get("MONGODB_URI")
ip = os.environ.get("BackendIP")
port = os.environ.get("Port")

mongoClient = MongoClient(uri)
database = mongoClient["Vista"]
collection = database["VistaCluster"]

sessionTokens = dict()

async def addSessionToken(username, token):
    sessionTokens[username] = token

    async def expireToken():
        await asyncio.sleep(86400)
        if username in sessionTokens.keys() and sessionTokens[username] == token:
            del sessionTokens[username]

    asyncio.create_task(expireToken())

def getData(path):
    data = collection.find()

    for document in data:
        if document["_id"] == path[0]:
            data = document
            break
    else:
        return None

    for key in path:
        if key in data.keys():
            data = data[key]
        else:
            return None
        
    return data

def setData(path, data):
    newData = collection.find_one({"_id":path[0]})
    if newData != None:
        newData = dict(newData)
        dataUpdate = newData
        
        for key in enumerate(path):
            if key[0] != len(path) - 1:
                if key[1] in dataUpdate.keys():
                    if isinstance(dataUpdate[key[1]], dict):
                        dataUpdate = dataUpdate[key[1]]
                    else:
                        dataUpdate[key[1]] = {}
                        dataUpdate = dataUpdate[key[1]]
                else:
                    dataUpdate[key[1]] = {}
                    dataUpdate = dataUpdate[key[1]]
        dataUpdate[path[-1]] = data
        collection.find_one_and_replace({"_id":path[0]}, newData)

    else:
        newData = {}
        dataUpdate = newData
        
        for key in enumerate(path):
            dataUpdate[key[1]] = {}
            if (key[0] != len(path) - 1):
                dataUpdate = dataUpdate[key[1]]
        dataUpdate[path[-1]] = data

        newData["_id"] = path[0]
        collection.insert_one(newData)

def delData(path):
    data = collection.find()

    target = path.pop()

    for document in data:
        if len(path) != 0:
            if document["_id"] == path[0]:
                doc = document
                data = doc
                for key in path:
                    if key in data.keys():
                        data = data[key]
                if target in data.keys():
                    del data[target]
                
                collection.find_one_and_replace({"_id":path[0]}, doc)
                break
        else:
            collection.delete_one({"_id":target})

USER_STATE = {}
"""
USER_STATE[websocket] = {
    "status": "idle" or "waiting" or "matched",
    "question": str or None,
    "answer": str or None,
    "partner": websocket or None
}
"""

WAITING_QUEUE = []

async def match_two_clients(client_a, client_b):
    USER_STATE[client_a]["status"] = "matched"
    USER_STATE[client_b]["status"] = "matched"

    await client_a.send(json.dumps({
        "response": "matchFound",
        "question": USER_STATE[client_b]["question"]
    }))
    await client_b.send(json.dumps({
        "response": "matchFound",
        "question": USER_STATE[client_a]["question"]
    }))

    USER_STATE[client_a]["partner"] = client_b
    USER_STATE[client_b]["partner"] = client_a

async def process_message(client, msg):
    mtype = msg.get("purpose")
    
    if mtype == "register":
        username = msg.get("username", "")
        password = msg.get("password", "")
        
        if getData(["Credentials", username]) == None:
            hash_object = hashlib.sha256()
            hash_object.update(password.encode())
            hashed_password = hash_object.hexdigest()
            setData(["Credentials", username, "password"], hashed_password)
            
            data = {"response": "registerSuccess",
                    "result": "Registration Successful! Please Sign In."}
        else:
            data = {"response": "usernameAlreadyTaken",
                    "result": "Username Already Taken!"}
        await client.send(json.dumps(data))
    elif mtype == "signIn":
        username = msg.get("username", "")
        password = msg.get("password", "")

        hash_object = hashlib.sha256()
        hash_object.update(password.encode())
        hashed_password = hash_object.hexdigest()
        
        if getData(["Credentials", username, "password"]) == hashed_password:
            sessionToken = str(uuid.uuid4())
            await addSessionToken(username, sessionToken)
            data = {"response": "signInSuccess",
                "sessionToken": sessionToken}
        else:
            data = {"response": "fail"}
        await client.send(json.dumps(data))
    elif mtype == "signOut":
        sessionID = data["sessionToken"]
        username = data["username"]

        if username in sessionTokens.keys() and sessionTokens[username] == sessionID:
            del sessionTokens[username]
            data = {"response": "signOutSuccess"}
        else:
            data = {"response": "fail"}
        await client.send(json.dumps(data))
    elif mtype == "askQuestion":
        if username in sessionTokens.keys() and sessionTokens[username] == sessionID:
            if USER_STATE[client]["status"] == "idle":
                question = msg.get("question", "")
                USER_STATE[client]["question"] = question
                USER_STATE[client]["status"] = "waiting"

                if WAITING_QUEUE:
                    other = WAITING_QUEUE.pop(0)
                    await match_two_clients(client, other)
                else:
                    WAITING_QUEUE.append(client)
                    await client.send(json.dumps({"response": "waiting"}))
            else:
                print("Client is not idle, ignoring question")
        else:
            data = {"response": "fail"}
        await client.send(json.dumps(data))

    elif mtype == "provideAnswer":
        if username in sessionTokens.keys() and sessionTokens[username] == sessionID:
            if USER_STATE[client]["status"] == "matched":
                USER_STATE[client]["answer"] = msg.get("answer", "")
                partner = USER_STATE[client].get("partner")

                if partner and USER_STATE[partner].get("answer") is not None:
                    your_answer = USER_STATE[client]["answer"]
                    partner_answer = USER_STATE[partner]["answer"]

                    await client.send(json.dumps({
                        "response": "answerReceived",
                        "answer": partner_answer
                    }))
                    await partner.send(json.dumps({
                        "response": "answerReceived",
                        "answer": your_answer
                    }))

                    USER_STATE[client].update({
                        "status": "idle",
                        "question": None,
                        "answer": None,
                        "partner": None
                    })
                    USER_STATE[partner].update({
                        "status": "idle",
                        "question": None,
                        "answer": None,
                        "partner": None
                    })
            else:
                print("Client is not matched, ignoring answer")
        else:
            data = {"response": "fail"}
        await client.send(json.dumps(data))
    else:
        print("Unknown Message")

async def client_handler(client):
    USER_STATE[client] = {
        "status": "idle",
        "question": None,
        "answer": None,
        "partner": None
    }

    try:
        async for raw_msg in client:
            try:
                msg = json.loads(raw_msg)
            except:
                await client.send(json.dumps({"error": "Invalid JSON"}))
                continue

            await process_message(client, msg)

    except websockets.ConnectionClosed:
        pass
    finally:
        if client in WAITING_QUEUE:
            WAITING_QUEUE.remove(client)

        partner = USER_STATE[client].get("partner")
        if partner:
            USER_STATE[partner]["partner"] = None
            USER_STATE[partner]["answer"] = None
            if USER_STATE[partner]["status"] == "matched":
                await partner.send(json.dumps({"response": "partnerDisconnected"}))
                USER_STATE[partner]["status"] = "idle"

        USER_STATE.pop(client, None)
        await client.close()

async def main():
    print(f"Server listening on {ip}:{port}")
    server = await websockets.serve(client_handler, ip, port)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
