import { StatusBar } from 'expo-status-bar';
import { View, Text, Image, ScrollView, TouchableOpacity, TextInput, Modal, SafeAreaView, ImageBackground } from "react-native";
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useState, useEffect } from 'react';
import LoadingScreen from './loading';
import LoginPage from './login';

type ClientState = 'idle' | 'waiting' | 'matched' | 'waiting_for_partner';
const socketAddress = 'ws://LocalHost:1134';

export default function Index() {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [clientState, setClientState] = useState<ClientState>('idle');
  const [previousState, setPreviousState] = useState<ClientState | null>(null);
  const [messageLog, setMessageLog] = useState<string[]>([]);
  const [isBouncing, setIsBouncing] = useState(false);

  const [isQuestion, setIsQuestion] = useState(true);

  // Modal States
  const [modalVisible, setModalVisible] = useState(false);
  const [modalMessage, setModalMessage] = useState('');

  // Websocket Constants
  const [ws, setWs] = useState<WebSocket | null>(null);

  // Connect on mount
  useEffect(() => {
    const socket = new WebSocket(socketAddress);

    socket.onopen = () => {
      console.log('Connected to server.');
      setWs(socket);
    };
    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleServerMessage(msg);
      } catch (err) {
        console.log('[Error] Invalid JSON received.');
      }
    };
    socket.onclose = () => {
      console.log('Connection closed by server.');
    };
    socket.onerror = (err) => {
      console.log(`[Error] ${JSON.stringify(err)}`);
    };

    return () => {
      socket.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Check for state changes
  useEffect(() => {
    if (isLoggedIn && clientState !== previousState) {
   
    if (clientState === 'waiting_for_partner') {
        showModal('Waiting for your partner to answer...');
      }
      setPreviousState(clientState);
    }
  }, [clientState, previousState, isLoggedIn]);

  function showModal(message: string) {
    setModalMessage(message);
    setModalVisible(true);
  }

  function hideModal() {
    setModalVisible(false);
  }

  function handleServerMessage(msg: any) {
    if (msg.response === 'waiting') {
      showModal('Waiting for a match...');
      setClientState('waiting');
      setIsBouncing(true);
      setIsQuestion(true);
    } else if (msg.response === 'matchFound') {
      showModal(`[Matched!] Partner's question: ${msg.question}`);
      setIsQuestion(false);
      setClientState('matched');
      setIsBouncing(true);
    } else if (msg.response === 'answerReceived') {
      showModal(`[Answer received!] Your partner's advice: ${msg.answer}`);
      setClientState('idle');
      setIsBouncing(false);
      setIsQuestion(true);
    } else if (msg.response === 'partnerDisconnected') {
      showModal('[Notification] Your partner disconnected.');
      setClientState('idle');
      setIsBouncing(false);
      setIsQuestion(true);
    } else if (msg.error) {
      showModal(`[Error] ${msg.error}`);
    } else {
      showModal(`[Server message] ${JSON.stringify(msg)}`);
    }
  }

  function sendJson(obj: any) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      showModal('Not connected or already closed.');
      return;
    }
    ws.send(JSON.stringify(obj));
  }

  const handleSubmit = () => {
    if (inputValue.trim()) {
      if (clientState === 'idle') {
        // askQuestion logic
        const msg = { purpose: 'askQuestion', question: inputValue };
        sendJson(msg);
        setClientState('waiting');
        setInputValue('');
        
      } else if (clientState === 'matched') {
        // provideAnswer logic
        const msg = { purpose: 'provideAnswer', answer: inputValue };
        sendJson(msg);
        setClientState('waiting_for_partner');
        setInputValue('');
      } else {
        showModal('waiting');
      }
    } else {
      showModal('Please enter text in the input field');
      setIsBouncing(false);
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (isLoggedIn ?
    <SafeAreaProvider>
      <ImageBackground source={require('../assets/images/homebg.png')} resizeMode="cover" className="flex-1">
        <StatusBar style="light" />
        <SafeAreaView>
          <View className="flex-col items-center justify-between py-6 shadow-md">
            <Text className="text-8xl font-bold text-white font-rubik">VISTA</Text>
            <View className="flex-row space-x-4">
              <Text className="text-white font-rubik text-4xl">Hello BLANK</Text>
            </View>
          </View>
          <TouchableOpacity
            onPress={handleSubmit}
            className={`${
              isBouncing ? 'animate-bounce' : ''
            } w-48 h-48 bg-white border-solid border-black border-4 rounded-full shadow-md flex items-center self-center justify-center mt-6 mb-10`}>
            <Image source={require('../assets/images/Logo.png')} className="w-32 h-32 self-center" />
          </TouchableOpacity>

          <View className="p-4 space-y-4">
            <View className="bg-white p-4 rounded-lg shadow-md h-32">
              <TextInput
                editable
                multiline
                numberOfLines={2}
                className="mt-3 text-gray-700 text-4xl"
                placeholder={`${isQuestion ? 'Ask a question...' : 'Provide a perspective...'}`}
                placeholderTextColor="rgba(0, 0, 0, 0.2)"
                value={inputValue}
                onChangeText={setInputValue}
                blurOnSubmit={true}
              />
            </View>
          </View>

        </SafeAreaView>

        {/* Bottom Navigation */}
        <View className="flex-row items-center justify-between px-16 py-6 bg-gray-800 shadow-md absolute bottom-0 left-0 right-0">
          <TouchableOpacity>
            <Image source={require('../assets/images/home.png')} className="w-10 h-10 tint-blue-500" />
          </TouchableOpacity>
          <TouchableOpacity>
            <Image source={require('../assets/images/add.png')} className="w-10 h-10" />
          </TouchableOpacity>
          <TouchableOpacity>
            <Image source={require('../assets/images/menu-burger.png')} className="w-10 h-10" />
          </TouchableOpacity>
        </View>
      </ImageBackground>

      {/* Modal for messages */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={hideModal}>
        <View className="flex-1 justify-center items-center bg-black bg-opacity-50">
          <View className="bg-white p-6 rounded-lg w-4/5 max-w-md">
            <Text className="text-center text-xl font-semibold">{modalMessage}</Text>
            <TouchableOpacity onPress={hideModal} className="bg-blue-500 py-2 px-4 rounded-lg mt-4">
              <Text className="text-white text-lg text-center">Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaProvider>
    :
    <SafeAreaProvider>
      <LoginPage setLoggedIn={setIsLoggedIn} />
    </SafeAreaProvider>
  );
}
