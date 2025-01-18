// Index.tsx
import { StatusBar } from 'expo-status-bar';
import { View, Text, Image, ScrollView, TouchableOpacity, TextInput, Button,Keyboard } from "react-native";
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { useState } from 'react';
import LoadingScreen from './loading';

export default function Index() {
  const [isLoading, setIsLoading] = useState(false);
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

  return (
    <SafeAreaProvider>
      <View className="flex-1 bg-gray-700">
        {/* Status Bar */}
        <StatusBar style="light" />

        {/* Header */}
        <SafeAreaView className="flex-row items-center justify-between px-4 py-3 bg-gray-800 shadow-md">
          <Text className="text-5xl font-bold text-blurple font-rubik">VISTA</Text>
          <View className="flex-row space-x-4">
            <Text className="text-white font-rubik text-xl">Hello Peter</Text>
          </View>
        </SafeAreaView>

        {/* Feed */}
        <SafeAreaView>
          <Image source={require('../assets/images/evil-larry-larry.png')} className="self-center" />
          <View className="p-4 space-y-4">
            {/* Post 1 */}
            <View className="bg-white p-4 rounded-lg shadow-md h-32">
              <TextInput
                editable
                multiline
                numberOfLines={2}
                className="mt-3 text-gray-700 text-4xl"
                placeholder="Ask a Question!"
                placeholderTextColor="rgba(0, 0, 0, 0.2)"
                value={inputValue}
                onChangeText={setInputValue} // Update input value state
                blurOnSubmit={true}
              />
            </View>
            <TouchableOpacity
                onPress={handleSubmit} // Trigger loading on submit button press
                className="mt-4 bg-blurple py-2 px-4 rounded"
              >
                <Text className="text-gray-300 text-center text-xl">Ask!</Text>
              </TouchableOpacity>
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
      </View>
    </SafeAreaProvider>
  );
}
