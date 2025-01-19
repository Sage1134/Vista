// note that when hosting on windows, it requires turning your firewall off.

import React, { useState } from 'react';
import { io } from 'socket.io-client';

import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Alert
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
// import { useVideoPlayer, VideoView } from 'expo-video';
import { Video, ResizeMode } from 'expo-av'; // Import the Video component and ResizeMode enum from expo-av

export default function LoginPage({setLoggedIn}:{setLoggedIn:React.Dispatch<React.SetStateAction<boolean>>}){
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const socket = io('ws://192.168.137.116:8080'); 

  const handleLogin = () => {
    if (email === '' || password === '') {
      Alert.alert('Error', 'Please fill out all fields.');
      return;
    }else{
      Alert.alert('Success', `Welcome, ${email}!`);
      setLoggedIn(true);
      socket.emit('login', email);
    }

  };

//   const player = useVideoPlayer(require("@/public/dancing.mp4"), player => {
//     player.loop = true;
//     player.play();
//   });

  return (
    <SafeAreaProvider>
        <View className='flex flex-1 justify-center items-center p-5 bg-gray-700'>        
            {/* <View style={{ flex: 1, position: "relative" }}> */}
                {/* Video Component */}
                <Video
                    source={require('@/assets/dancing-video-darkened.mp4')} // Path to your video file
                    style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }} // Full screen positioning
                    shouldPlay
                    isLooping
                    isMuted
                    resizeMode={ResizeMode.COVER}
                />


            <SafeAreaView className="flex-row justify-center px-4 py-3">
              <Text className="text-8xl font-bold text-blurple font-rubik">VISTA</Text>
            </SafeAreaView>
            <Text className='text-2xl font-bold mb-10 text-white'>See a new perspective.</Text>

            <TextInput
                className="w-full h-12 border border-gray-300 rounded-lg px-2.5 mb-5 bg-white"
                placeholder="Email"
                keyboardType="email-address"
                value={email}
                onChangeText={setEmail}
            />

            <TextInput
                className="w-full h-12 border border-gray-300 rounded-lg px-2.5 mb-5 bg-white"
                placeholder="Password"
                secureTextEntry
                value={password}
                onChangeText={setPassword}
            />

            <TouchableOpacity className="w-full h-12 bg-blurple flex justify-center items-center rounded-lg" onPress={handleLogin}>
                <Text className="text-white text-lg font-bold">Login</Text>
            </TouchableOpacity>

            <TouchableOpacity className="w-full h-12 bg-white flex justify-center items-center rounded-lg mt-2" onPress={handleLogin}>
                <Text className="text-blurple text-lg font-bold">No Account? Sign Up Today!</Text>
            </TouchableOpacity>
        </View>
    </SafeAreaProvider>
  );
};
