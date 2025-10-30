import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { getCostSummary, getOptimizationOpportunities, makeTrackedRequest } from '../services/api';
import LoadingSpinner from './LoadingSpinner';

const CostAnalytics = () => {
  const [agentId, setAgentId] = useState('agent-001');
  const [costData, setCostData] = useState(null);
  const [optimizations, setOptimizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testPrompt, setTestPrompt] = useState('Explain quantum computing in simple terms');
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    fetchCostAnalytics();
  }, [agentId]);

  const fetchCostAnalytics = async () => {
    try {
      setLoading(true);
      const [cost, optimizationOps] = await Promise.all([
        getCostSummary(agentId, 24),
        getOptimizationOpportunities(agentId)
      ]);
      
      setCostData(cost);
      setOptimizations(optimizationOps);
    } catch (error) {
      console.error('Failed to fetch cost analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTestRequest = async () => {
    try {
      const result = await makeTrackedRequest(agentId, testPrompt);
      setTestResult(result);
      await fetchCostAnalytics(); // Refresh data after test
    } catch (error) {
      console.error('Test request failed:', error);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading cost analytics..." />;
  }

  const mockUsageData = [
    { model: 'gemini-pro', requests: costData?.request_count || 25, cost: costData?.total_cost || 0.15 },
    { model: 'gemini-flash', requests: 8, cost: 0.032 },
    { model: 'gemini-ultra', requests: 3, cost: 0.089 }
  ];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cost Analytics</h1>
          <p className="text-gray-600 mt-1">Detailed cost analysis and optimization insights</p>
        </div>
        
        <select
          value={agentId}
          onChange={(e) => setAgentId(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        >
          <option value="agent-001">Agent-001</option>
          <option value="agent-002">Agent-002</option>
          <option value="agent-003">Agent-003</option>
        </select>
      </div>

      {/* Cost Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-sm font-medium text-gray-600 mb-1">Total Requests (24h)</h3>
          <p className="text-2xl font-bold text-gray-900">{costData?.request_count || 0}</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-sm font-medium text-gray-600 mb-1">Total Cost (24h)</h3>
          <p className="text-2xl font-bold text-gray-900">${costData?.total_cost?.toFixed(4) || '0.0000'}</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-sm font-medium text-gray-600 mb-1">Avg Cost/Request</h3>
          <p className="text-2xl font-bold text-gray-900">${costData?.average_cost_per_request?.toFixed(4) || '0.0000'}</p>
        </div>
        
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-sm font-medium text-gray-600 mb-1">Total Tokens</h3>
          <p className="text-2xl font-bold text-gray-900">{costData?.total_tokens?.toLocaleString() || 0}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Model Usage Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage by Model</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockUsageData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="model" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="requests" fill="#3b82f6" name="Requests" />
              <Bar yAxisId="right" dataKey="cost" fill="#10b981" name="Cost ($)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost Distribution */}
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={mockUsageData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="cost"
                label={({model, cost}) => `${model}: $${cost.toFixed(3)}`}
              >
                {mockUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`$${value.toFixed(4)}`, 'Cost']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Test AI Request */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Test AI Request with Cost Tracking</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Prompt
            </label>
            <textarea
              value={testPrompt}
              onChange={(e) => setTestPrompt(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows="3"
              placeholder="Enter a test prompt..."
            />
          </div>
          
          <button
            onClick={handleTestRequest}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Send Test Request
          </button>
          
          {testResult && (
            <div className="mt-4 space-y-3">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-medium text-gray-900 mb-2">Response:</h4>
                <p className="text-gray-700 text-sm">{testResult.response}</p>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-xs text-blue-600 font-medium">Tokens Used</p>
                  <p className="text-lg font-bold text-blue-900">{testResult.metrics?.tokens_used || 0}</p>
                </div>
                
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-xs text-green-600 font-medium">Cost</p>
                  <p className="text-lg font-bold text-green-900">${testResult.metrics?.cost_usd?.toFixed(6) || '0.000000'}</p>
                </div>
                
                <div className="bg-purple-50 p-3 rounded-lg">
                  <p className="text-xs text-purple-600 font-medium">Response Time</p>
                  <p className="text-lg font-bold text-purple-900">{testResult.metrics?.response_time_ms || 0}ms</p>
                </div>
                
                <div className="bg-yellow-50 p-3 rounded-lg">
                  <p className="text-xs text-yellow-600 font-medium">Model</p>
                  <p className="text-lg font-bold text-yellow-900">{testResult.metrics?.model_name || 'N/A'}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Optimization Opportunities */}
      <div className="bg-white p-6 rounded-xl shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Opportunities</h3>
        
        {optimizations.length > 0 ? (
          <div className="space-y-3">
            {optimizations.map((opp, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900">{opp.rule_name}</h4>
                    <p className="text-sm text-gray-600 mt-1">Action: {opp.action}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-green-600">
                      Potential Savings: ${opp.estimated_savings?.toFixed(4) || '0.0000'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No optimization opportunities detected at this time.</p>
        )}
      </div>
    </div>
  );
};

export default CostAnalytics;
