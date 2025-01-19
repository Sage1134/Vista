// Index.tsx
import { StatusBar } from 'expo-status-bar';
import { 
  View, 
  Text, 
  Image, 
  ScrollView, 
  TouchableOpacity, 
  TextInput, 
  Button,
  Keyboard, 
  ImageBackground,
  TouchableWithoutFeedback, Animated 
} from "react-native";
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import React, { useState, useRef } from 'react';
import LoadingScreen from './loading';
import LoginPage from './login';



export default function Index() {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(true); // set to false when done testing
  const [inputValue, setInputValue] = useState('');
  const [savedText, setSavedText] = useState('');

  // This function will be triggered when the user clicks the "Submit" button
  const handleSubmit = () => {
    if (inputValue.trim()) {  // Check if there's any input value
      setIsLoading(true); // Set loading state to true when the user submits
      setSavedText(inputValue); // Save the input text
      setTimeout(() => {
        setIsLoading(false); // Set loading state back to false after a delay (simulating an API call or process)
      }, 2000); // Simulating a delay of 2 seconds
    } else {
      alert('Please enter a question'); 
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  const AnimatedButton = () => {
    const scaleValue = useRef(new Animated.Value(1)).current;
  
    const handlePressIn = () => {
      Animated.spring(scaleValue, {
        toValue: 1.25, // Scale up
        useNativeDriver: true,
      }).start();
    };
  
    const handlePressOut = () => {
      Animated.spring(scaleValue, {
        toValue: 1, // Scale back to normal
        useNativeDriver: true,
      }).start();
    };
  
    return (
      <TouchableWithoutFeedback
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        // onPress={handleSubmit} // Add your handler here
      >
        <Animated.View
          style={{
            transform: [{ scale: scaleValue }],
            marginTop: 16,
            paddingVertical: 8,
            paddingHorizontal: 16,
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Image
            source={require('../assets/images/Logo.png')}
            style={{ width: 140, height: 140, borderRadius: 70, backgroundColor: 'white' }}
            fadeDuration={0}
          />
        </Animated.View>
      </TouchableWithoutFeedback>
    );
  };

  return ( isLoggedIn ?
    <SafeAreaProvider>
      <ImageBackground source={require("../assets/images/bg-swishes.png")} resizeMode='cover' className='w-full h-full'>
        <View className="flex-1">
          {/* Status Bar */}
          <StatusBar style="light" />

          {/* Header */}
          {/* <SafeAreaView className="flex-row items-center justify-between px-4 py-3 bg-gray-800 shadow-md">
            <Text className="text-5xl font-bold text-blurple font-rubik">VISTA</Text>
            <View className="flex-row space-x-4">
              <Text className="text-white font-rubik text-xl">Hello Peter</Text>
            </View>
          </SafeAreaView> */}

          {/* Feed */}
          <SafeAreaView className='my-auto'>
            {/* <Image source={require('../assets/images/evil-larry-larry.png')} className="self-center" /> */}
            <View className="p-4 space-y-4">
              {/* Post 1 */}
              <View className="bg-white p-4 rounded-lg shadow-md h-17">
                <TextInput
                  editable
                  multiline
                  numberOfLines={4}
                  className="text-gray-700 text-xl text-center"
                  placeholder="Ask a Question!"
                  placeholderTextColor="rgba(0, 0, 0, 0.2)"
                  value={inputValue}
                  onChangeText={setInputValue} // Update input value state
                  blurOnSubmit={true}
                />
              </View>
              <AnimatedButton />

            </View>
          </SafeAreaView>

          {/* Bottom Navigation */}
          <View className="flex-row items-center justify-between px-16 py-6 absolute bottom-0 left-0 right-0 ">
            <TouchableOpacity>
              <Image source={require('../assets/images/home.png')} className="w-10 h-10 tint-blue-500" tintColor={"white"} />
            </TouchableOpacity>
            <TouchableOpacity>
              <Image source={require('../assets/images/add.png')} className="w-10 h-10" tintColor={"white"} />
            </TouchableOpacity>
            <TouchableOpacity>
              <Image source={require('../assets/images/menu-burger.png')} className="w-10 h-10" tintColor={"white"} />
            </TouchableOpacity>
          </View>
        </View>
      </ImageBackground>

    </SafeAreaProvider>
    :
    <SafeAreaProvider>
      <LoginPage setLoggedIn={setIsLoggedIn}/>
    </SafeAreaProvider> 
  );
}
