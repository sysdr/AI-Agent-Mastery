import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8080';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: 10000,
    });

    // Add request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && !error.config._retry) {
          error.config._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              localStorage.setItem('access_token', response.access_token);
              
              // Retry the original request
              error.config.headers.Authorization = `Bearer ${response.access_token}`;
              return this.client.request(error.config);
            }
          } catch (refreshError) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  async login(username, password) {
    const response = await this.client.post('/auth/login', {
      username,
      password
    });
    return response.data;
  }

  async refreshToken(refreshToken) {
    const response = await this.client.post('/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  }

  async validateToken(token) {
    try {
      await this.client.get('/health', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return true;
    } catch {
      return false;
    }
  }

  async getMetrics() {
    const response = await this.client.get('/metrics');
    return response.data;
  }

  async getHealth() {
    const response = await this.client.get('/health');
    return response.data;
  }

  async testApiEndpoint(endpoint, method = 'GET', data = null) {
    const config = { method, url: `/api/${endpoint}` };
    if (data) config.data = data;
    
    const response = await this.client.request(config);
    return response.data;
  }
}

const apiService = new ApiService();
export default apiService;
