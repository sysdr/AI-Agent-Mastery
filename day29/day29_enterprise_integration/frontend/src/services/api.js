import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const api = {
  // Integration endpoints
  getCustomer: async (customerId) => {
    const response = await axiosInstance.get(`/integration/customer/${customerId}`);
    return response.data;
  },

  updateCustomer: async (customerId, data) => {
    const response = await axiosInstance.put(`/integration/customer/${customerId}`, data);
    return response.data;
  },

  getIntegrationStats: async () => {
    const response = await axiosInstance.get('/integration/stats');
    return response.data;
  },

  // Legacy system endpoints
  getLegacyHealth: async () => {
    const response = await axiosInstance.get('/legacy/health');
    return response.data;
  },

  setLegacyHealth: async (healthy) => {
    const response = await axiosInstance.post('/legacy/health', { healthy });
    return response.data;
  },

  // Audit endpoints
  getAuditEvents: async (filters = {}) => {
    const response = await axiosInstance.get('/audit/events', { params: filters });
    return response.data;
  }
};
