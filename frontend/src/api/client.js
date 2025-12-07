import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const client = axios.create({
  baseURL: 'https://example.pgsystem.com/api/',
});

client.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  const tenantId = await AsyncStorage.getItem('tenantId');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  return config;
});

export default client;
