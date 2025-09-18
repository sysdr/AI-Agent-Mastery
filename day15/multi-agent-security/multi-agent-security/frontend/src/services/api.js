import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const agentAPI = {
  createAgent: (data) => api.post('/agents', data),
  listAgents: () => api.get('/agents'),
  getAgentMessages: (agentId) => api.get(`/agents/${agentId}/messages`),
  getAgentUsage: (agentId) => api.get(`/agents/${agentId}/usage`),
};

export const contentAPI = {
  createContent: (data) => api.post('/content/create', data),
  reviewContent: (contentId) => api.post(`/content/${contentId}/review`),
  finalReviewContent: (contentId) => api.post(`/content/${contentId}/final-review`),
};

export const taskAPI = {
  assignTask: (data) => api.post('/tasks/assign', data),
};

export const systemAPI = {
  getStatus: () => api.get('/system/status'),
};

export default api;
