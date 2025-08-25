import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
  }

  async executeCommand(command, parameters) {
    const response = await this.client.post('/agent/execute', {
      command,
      parameters
    });
    return response.data;
  }

  async getCapabilities() {
    const response = await this.client.get('/agent/capabilities');
    return response.data;
  }

  async getPermissions() {
    const response = await this.client.get('/security/permissions');
    return response.data;
  }

  async getAuditLogs() {
    const response = await this.client.get('/security/audit');
    return response.data;
  }

  async getToolRegistry() {
    const response = await this.client.get('/tools/registry');
    return response.data;
  }
}

export default new ApiService();
