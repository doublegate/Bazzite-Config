/**
 * Bazzite Optimizer Mobile App
 * React Native companion app for real-time gaming system monitoring
 */

import React, {useEffect, useState} from 'react';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {Provider as PaperProvider, DefaultTheme} from 'react-native-paper';

// Screens
import DashboardScreen from './src/screens/DashboardScreen';
import ProfilesScreen from './src/screens/ProfilesScreen';
import AlertsScreen from './src/screens/AlertsScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import PairingScreen from './src/screens/PairingScreen';

// Services
import {WebSocketService} from './src/services/WebSocketService';
import {StorageService} from './src/services/StorageService';

const Tab = createBottomTabNavigator();

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#6200ee',
    accent: '#03dac4',
    background: '#121212',
    surface: '#1e1e1e',
    text: '#ffffff',
    error: '#cf6679',
  },
  dark: true,
};

function App(): JSX.Element {
  const [isPaired, setIsPaired] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if device is already paired
    checkPairingStatus();
  }, []);

  const checkPairingStatus = async () => {
    try {
      const deviceToken = await StorageService.getDeviceToken();
      setIsPaired(!!deviceToken);

      if (deviceToken) {
        // Auto-connect WebSocket
        const deviceId = await StorageService.getDeviceId();
        WebSocketService.connect(deviceId, deviceToken);
      }
    } catch (error) {
      console.error('Error checking pairing status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePairingComplete = async (token: string, deviceId: string) => {
    await StorageService.saveDeviceToken(token);
    await StorageService.saveDeviceId(deviceId);
    setIsPaired(true);

    // Connect WebSocket
    WebSocketService.connect(deviceId, token);
  };

  if (isLoading) {
    return null; // TODO: Add loading screen
  }

  if (!isPaired) {
    return (
      <SafeAreaProvider>
        <PaperProvider theme={theme}>
          <PairingScreen onPairingComplete={handlePairingComplete} />
        </PaperProvider>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <PaperProvider theme={theme}>
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={({route}) => ({
              tabBarIcon: ({focused, color, size}) => {
                let iconName = 'home';

                if (route.name === 'Dashboard') {
                  iconName = 'view-dashboard';
                } else if (route.name === 'Profiles') {
                  iconName = 'cog-outline';
                } else if (route.name === 'Alerts') {
                  iconName = 'bell-outline';
                } else if (route.name === 'Settings') {
                  iconName = 'settings-outline';
                }

                return <Icon name={iconName} size={size} color={color} />;
              },
              tabBarActiveTintColor: theme.colors.primary,
              tabBarInactiveTintColor: 'gray',
              tabBarStyle: {
                backgroundColor: theme.colors.surface,
                borderTopColor: theme.colors.surface,
              },
              headerStyle: {
                backgroundColor: theme.colors.surface,
              },
              headerTintColor: theme.colors.text,
            })}>
            <Tab.Screen name="Dashboard" component={DashboardScreen} />
            <Tab.Screen name="Profiles" component={ProfilesScreen} />
            <Tab.Screen name="Alerts" component={AlertsScreen} />
            <Tab.Screen name="Settings" component={SettingsScreen} />
          </Tab.Navigator>
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
}

export default App;
