import axios from 'axios';

const API_BASE = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const fetchNetworkStatus = async () => {
  try {
    const response = await api.get('/api/network/status');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch network status:', error);
    throw error;
  }
};

export const solveProblem = async (problemData) => {
  try {
    const response = await api.post('/api/network/solve', problemData);
    return response.data;
  } catch (error) {
    console.error('Failed to solve problem:', error);
    throw error;
  }
};

export default api;
