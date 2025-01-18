import React from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';


export default function LoadingScreen() {
    return (
        <View className='flex-1 items-center justify-center bg-gray-700'>
            <ActivityIndicator className='size-5' />
        </View>
    );
}