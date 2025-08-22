import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const agentService = {
  getStatus: () => api.get('/status'),
  sendMessage: (message, context) => api.post('/chat', { message, context }),
  getHealth: () => api.get('/health'),
};

export default api;
