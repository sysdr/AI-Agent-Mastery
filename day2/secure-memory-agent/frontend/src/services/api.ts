import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Dashboard
  getDashboardMetrics: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },

  // Conversations
  createConversation: async (userId: string, title?: string) => {
    const response = await api.post('/memory/conversations', null, {
      params: { user_id: userId, title }
    });
    return response.data;
  },

  addMessage: async (message: { content: string; role: string; conversation_id: string }) => {
    const response = await api.post('/memory/messages', message);
    return response.data;
  },

  getConversationMessages: async (conversationId: string, limit?: number) => {
    const response = await api.get(`/memory/conversations/${conversationId}/messages`, {
      params: { limit }
    });
    return response.data;
  },

  getOptimizedContext: async (conversationId: string, maxTokens?: number) => {
    const response = await api.get(`/memory/conversations/${conversationId}/context`, {
      params: { max_tokens: maxTokens }
    });
    return response.data;
  },

  // Security
  analyzePII: async (text: string) => {
    const response = await api.post('/security/pii-analysis', { text });
    return response.data;
  },

  testEncryption: async (text: string, conversationId: string) => {
    const response = await api.post('/security/encryption-test', { text, conversation_id: conversationId });
    return response.data;
  },

  getSecurityEvents: async (limit?: number, securityLevel?: string) => {
    const response = await api.get('/analytics/security-events', {
      params: { limit, security_level: securityLevel }
    });
    return response.data;
  },

  healthCheck: async () => {
    const response = await api.get('/security/health-check');
    return response.data;
  }
};
