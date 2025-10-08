import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1' 
  : 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Agent management
  async registerAgent(agentData) {
    const response = await apiClient.post('/agents/register', agentData);
    return response.data;
  },

  // Security operations
  async getSecurityStatus() {
    const response = await apiClient.get('/security/status');
    return response.data;
  },

  async runSecurityScan() {
    const response = await apiClient.post('/security/scan');
    return response.data;
  },

  async getVulnerabilities() {
    const response = await apiClient.get('/security/vulnerabilities');
    return response.data;
  },

  // Audit operations
  async getAuditEntries(params = {}) {
    const response = await apiClient.get('/audit/entries', { params });
    return response.data;
  },

  // Performance metrics
  async getPerformanceMetrics() {
    const response = await apiClient.get('/metrics/performance');
    return response.data;
  },

  async getDashboardData() {
    const response = await apiClient.get('/metrics/dashboard');
    return response.data;
  }
};

export default apiService;
