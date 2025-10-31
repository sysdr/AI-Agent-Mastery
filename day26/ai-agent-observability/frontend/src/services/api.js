import axios from 'axios';

// Use proxy in package.json for development, or explicit URL for production
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const metricsAPI = {
  getRealtime: async () => {
    const response = await api.get('/api/metrics/realtime');
    return response.data;
  },
  recordConfidence: async (agentId, confidence, context) => {
    const response = await api.post(`/api/metrics/confidence?agent_id=${agentId}&confidence=${confidence}`, context || {});
    return response.data;
  },
  recordRequest: async (agentType, status, responseTime) => {
    const response = await api.post(`/api/metrics/request?agent_type=${agentType}&status=${status}&response_time=${responseTime}`);
    return response.data;
  },
};

export const tracesAPI = {
  getAll: async (limit = 50) => {
    const response = await api.get(`/api/traces/?limit=${limit}`);
    return response.data;
  },
  getById: async (traceId) => {
    const response = await api.get(`/api/traces/${traceId}`);
    return response.data;
  },
  start: async (operation, metadata) => {
    const response = await api.post(`/api/traces/start?operation=${operation}`, metadata || {});
    return response.data;
  },
};

export const logsAPI = {
  getAll: async (level, startTime, limit = 100) => {
    const params = { limit };
    if (level) params.level = level;
    if (startTime) params.start_time = startTime;
    const response = await api.get('/api/logs/', { params });
    return response.data;
  },
  search: async (query, limit = 50) => {
    const response = await api.get(`/api/logs/search?query=${query}&limit=${limit}`);
    return response.data;
  },
};

export const operationsAPI = {
  getAll: async (status, limit = 50) => {
    const params = { limit };
    if (status) params.status = status;
    const response = await api.get('/api/operations/', { params });
    return response.data;
  },
  getById: async (operationId) => {
    const response = await api.get(`/api/operations/${operationId}`);
    return response.data;
  },
};

export const securityAPI = {
  getAlerts: async (severity) => {
    const params = {};
    if (severity) params.severity = severity;
    const response = await api.get('/api/security/alerts', { params });
    return response.data;
  },
  getThreatSummary: async (hours = 24) => {
    const response = await api.get(`/api/security/summary?hours=${hours}`);
    return response.data;
  },
};

export default api;

