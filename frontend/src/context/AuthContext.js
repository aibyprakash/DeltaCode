import React, { createContext, useContext, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import client from '../api/client';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  const login = async (email, password, tenantId) => {
    setLoading(true);
    try {
      if (tenantId) await AsyncStorage.setItem('tenantId', tenantId);
      const response = await client.post('auth/login/', { username: email, password });
      const { access, refresh } = response.data;
      await AsyncStorage.setItem('token', access);
      await AsyncStorage.setItem('refresh', refresh);
      // In production decode token to get role and tenant; here we mock user role
      setUser({ email, role: 'OWNER', tenantId });
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    await AsyncStorage.multiRemove(['token', 'refresh', 'tenantId']);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
