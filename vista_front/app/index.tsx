// Index.tsx
import { StatusBar } from 'expo-status-bar';
import { View, Text, Image, ScrollView, TouchableOpacity, TextInput, Platform,KeyboardAvoidingView, Alert, ImageBackground} from "react-native";
import { useState, useEffect } from 'react';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import LoadingScreen from './loading';
import LoginPage from './login';


export default function Index() {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [savedText, setSavedText] = useState('');
  const [message, setMessage] = useState<string>('');


  
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

  return ( isLoggedIn ?
    <SafeAreaProvider>
      <ImageBackground source={require('../assets/images/homebg.png')} resizeMode="cover" className="flex-1">
        {/* Status Bar */}
        <StatusBar style="light" />

        {/* Feed */}
        <SafeAreaView>
          <View className="flex-col items-center justify-between py-6 shadow-md">
            <Text className="text-8xl font-bold text-white font-rubik">VISTA</Text>
            <View className="flex-row space-x-4">
              <Text className="text-white font-rubik text-4xl">Hello BLANK</Text>
            </View>
          </View>
          <TouchableOpacity
                  onPress={handleSubmit} // Trigger loading on submit button press
                  className='w-48 h-48 bg-white border-solid border-black border-4 rounded-full shadow-md flex items-center self-center justify-center mt-6 mb-10'>
            <Image source={require('../assets/images/Logo.png')} className=" w-32 h-32 self-center" />
          </TouchableOpacity>

          <View
      className="p-4 space-y-4"
    >
      <View className="bg-white p-4 rounded-lg shadow-md h-32">
        <TextInput
          editable
          multiline
          numberOfLines={2}
          className="mt-3 text-gray-700 text-4xl"
          placeholder="Ask a Question!"
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
    </SafeAreaProvider>
    :
    <SafeAreaProvider>
      <LoginPage setLoggedIn={setIsLoggedIn}/>
    </SafeAreaProvider> 
  );
}
