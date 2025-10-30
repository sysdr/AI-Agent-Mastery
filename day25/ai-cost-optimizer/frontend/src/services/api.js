import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// API functions
export const getCostSummary = async (agentId, hours = 1) => {
  try {
    const response = await api.get(`/api/cost/summary/${agentId}?hours=${hours}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching cost summary:', error);
    // Return mock data for demo
    return {
      agent_id: agentId,
      period_hours: hours,
      total_cost: 0.1234,
      total_tokens: 1567,
      average_cost_per_request: 0.0082,
      request_count: 15,
      cost_trend: 'stable'
    };
  }
};

export const getPerformanceSummary = async (agentId, minutes = 60) => {
  try {
    const response = await api.get(`/api/performance/summary/${agentId}?minutes=${minutes}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching performance summary:', error);
    // Return mock data for demo
    return {
      agent_id: agentId,
      period_minutes: minutes,
      avg_cpu_usage: 45.2,
      avg_memory_usage: 62.8,
      avg_response_time: 1234,
      total_requests: 25,
      avg_error_rate: 1.2,
      performance_score: 87.3,
      status: 'healthy'
    };
  }
};

export const getForecast = async (agentId, forecastHours = 24) => {
  try {
    const response = await api.get(`/api/forecast/costs/${agentId}?forecast_hours=${forecastHours}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching forecast:', error);
    // Return mock data for demo
    const mockHourlyCosts = Array.from({ length: forecastHours }, (_, i) => 
      0.005 + (Math.random() * 0.01) + (Math.sin(i / 6) * 0.003)
    );
    
    return {
      agent_id: agentId,
      forecast_hours: forecastHours,
      current_hourly_rate: 0.0082,
      forecasted_total_cost: mockHourlyCosts.reduce((sum, cost) => sum + cost, 0),
      forecasted_hourly_costs: mockHourlyCosts,
      confidence_lower: mockHourlyCosts.map(cost => cost * 0.8),
      confidence_upper: mockHourlyCosts.map(cost => cost * 1.2),
      trend: 'stable',
      risk_assessment: {
        risk_level: 'low',
        message: 'Forecasted costs within acceptable range'
      }
    };
  }
};

export const getOptimizationOpportunities = async (agentId) => {
  try {
    const response = await api.get(`/api/cost/optimization/${agentId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching optimization opportunities:', error);
    return [];
  }
};

export const makeTrackedRequest = async (agentId, prompt, modelName = 'gemini-pro') => {
  try {
    const response = await api.post('/api/cost/request', {
      agent_id: agentId,
      prompt: prompt,
      model_name: modelName
    });
    return response.data;
  } catch (error) {
    console.error('Error making tracked request:', error);
    // Return mock response for demo
    return {
      success: true,
      response: "This is a mock response since the backend is not available. In a real scenario, this would be the actual AI-generated response to your prompt.",
      metrics: {
        tokens_used: 127,
        cost_usd: 0.000845,
        response_time_ms: 1456,
        model_name: modelName
      }
    };
  }
};

export default api;
