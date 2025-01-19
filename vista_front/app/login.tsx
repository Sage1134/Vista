import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TextInput, Button, ScrollView, StyleSheet } from 'react-native';

type ClientState = 'idle' | 'waiting' | 'matched' | 'waiting_for_partner';
const socketAddress = 'ws://100.66.219.46:1134';

export default function ClientApp() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [clientState, setClientState] = useState<ClientState>('idle');
  const [previousState, setPreviousState] = useState<ClientState | null>(null);
  const [messageLog, setMessageLog] = useState<string[]>([]);
  const [inputText, setInputText] = useState('');

  // Connect on mount
  useEffect(() => {
    const socket = new WebSocket(socketAddress);

    socket.onopen = () => {
      logMessage('Connected to server.');
      setWs(socket);
    };
    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleServerMessage(msg);
      } catch (err) {
        logMessage('[Error] Invalid JSON received.');
      }
    };
    socket.onclose = () => {
      logMessage('Connection closed by server.');
    };
    socket.onerror = (err) => {
      logMessage(`[Error] ${JSON.stringify(err)}`);
    };

    return () => {
      socket.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Check for state changes
  useEffect(() => {
    if (clientState !== previousState) {
      // Simulate client.py's while loop detection
      if (clientState === 'idle') {
        logMessage('Enter your question and press Send');
      } else if (clientState === 'matched') {
        logMessage('Enter your answer and press Send');
      } else if (clientState === 'waiting_for_partner') {
        logMessage('Waiting for your partner to answer...');
      }
      setPreviousState(clientState);
    }
  }, [clientState, previousState]);

  function handleServerMessage(msg: any) {
    if (msg.response === 'waiting') {
      logMessage('Waiting for a match...');
      setClientState('waiting');
    } else if (msg.response === 'matchFound') {
      logMessage(`[Matched!] Partner's question: ${msg.question}`);
      setClientState('matched');
    } else if (msg.response === 'answerReceived') {
      logMessage(`[Answer received!] Your partner's advice: ${msg.answer}`);
      setClientState('idle');
    } else if (msg.response === 'partnerDisconnected') {
      logMessage('[Notification] Your partner disconnected.');
      setClientState('idle');
    } else if (msg.error) {
      logMessage(`[Error] ${msg.error}`);
    } else {
      logMessage(`[Server message] ${JSON.stringify(msg)}`);
    }
  }

  function logMessage(message: string) {
    setMessageLog((prev) => [...prev, message]);
  }

  function sendJson(obj: any) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      logMessage('Not connected or already closed.');
      return;
    }
    ws.send(JSON.stringify(obj));
  }

  function handleSend() {
    if (clientState === 'idle') {
      // askQuestion
      const msg = { purpose: 'askQuestion', question: inputText };
      sendJson(msg);
      setClientState('waiting');
      setInputText('');
    } else if (clientState === 'matched') {
      // provideAnswer
      const msg = { purpose: 'provideAnswer', answer: inputText };
      sendJson(msg);
      setClientState('waiting_for_partner');
      setInputText('');
    } else {
      logMessage('Cannot send now. Currently waiting or in invalid state.');
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>QuestionClient (TSX)</Text>
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder={clientState === 'idle' ? 'Enter your question...' : 'Enter your answer...'}
          value={inputText}
          onChangeText={setInputText}
        />
        <Button title="Send" onPress={handleSend} />
      </View>
      <Text style={styles.stateText}>State: {clientState}</Text>
      <ScrollView style={styles.logBox}>
        {messageLog.map((line, idx) => (
          <Text key={idx} style={styles.logText}>
            {line}
          </Text>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    flex: 1,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 18,
    marginBottom: 12,
    fontWeight: 'bold',
  },
  inputRow: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  input: {
    flex: 1,
    borderColor: '#aaa',
    borderWidth: 1,
    marginRight: 8,
    padding: 5,
  },
  stateText: {
    marginBottom: 8,
    fontStyle: 'italic',
  },
  logBox: {
    flex: 1,
    marginTop: 10,
    backgroundColor: '#f0f0f0',
    padding: 8,
  },
  logText: {
    marginVertical: 2,
    fontSize: 14,
  },
});