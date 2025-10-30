import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { DollarSign, TrendingUp, Zap, AlertTriangle } from 'lucide-react';
import { getCostSummary, getPerformanceSummary, getForecast } from '../services/api';
import MetricCard from './MetricCard';
import LoadingSpinner from './LoadingSpinner';

const Dashboard = () => {
  const [agentId, setAgentId] = useState('agent-001');
  const [costData, setCostData] = useState(null);
  const [perfData, setPerfData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [agentId]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [cost, performance, forecast] = await Promise.all([
        getCostSummary(agentId, 24),
        getPerformanceSummary(agentId, 60),
        getForecast(agentId, 24)
      ]);
      
      setCostData(cost);
      setPerfData(performance);
      setForecastData(forecast);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateChartData = () => {
    if (!forecastData || !forecastData.forecasted_hourly_costs) return [];
    
    return forecastData.forecasted_hourly_costs.map((cost, index) => ({
      hour: `H+${index + 1}`,
      cost: cost,
      confidence_lower: forecastData.confidence_lower?.[index] || cost * 0.8,
      confidence_upper: forecastData.confidence_upper?.[index] || cost * 1.2
    }));
  };

  if (loading && !costData) {
    return <LoadingSpinner message="Loading dashboard data..." />;
  }

  const chartData = generateChartData();

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cost Optimization Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor and optimize AI agent costs and performance
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="agent-001">Agent-001</option>
            <option value="agent-002">Agent-002</option>
            <option value="agent-003">Agent-003</option>
          </select>
          
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Cost (24h)"
          value={`$${costData?.total_cost?.toFixed(4) || '0.0000'}`}
          change={costData?.cost_trend === 'increasing' ? '+12.5%' : costData?.cost_trend === 'decreasing' ? '-8.3%' : '0%'}
          changeType={costData?.cost_trend === 'increasing' ? 'increase' : costData?.cost_trend === 'decreasing' ? 'decrease' : 'neutral'}
          icon={DollarSign}
          color="blue"
        />
        
        <MetricCard
          title="Performance Score"
          value={`${perfData?.performance_score || 85}/100`}
          change="+2.1%"
          changeType="increase"
          icon={Zap}
          color="green"
        />
        
        <MetricCard
          title="Cost Forecast (24h)"
          value={`$${forecastData?.forecasted_total_cost?.toFixed(4) || '0.0000'}`}
          change={forecastData?.trend === 'increasing' ? 'Trending Up' : forecastData?.trend === 'decreasing' ? 'Trending Down' : 'Stable'}
          changeType={forecastData?.trend === 'increasing' ? 'increase' : forecastData?.trend === 'decreasing' ? 'decrease' : 'neutral'}
          icon={TrendingUp}
          color="purple"
        />
        
        <MetricCard
          title="Optimization Opportunities"
          value="3"
          change="New alerts"
          changeType="warning"
          icon={AlertTriangle}
          color="yellow"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Forecast Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Cost Forecast (24h)</h3>
            <span className="text-sm text-gray-500">Next 24 hours</span>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="hour" 
                stroke="#6b7280"
                fontSize={12}
              />
              <YAxis 
                stroke="#6b7280"
                fontSize={12}
                tickFormatter={(value) => `$${value.toFixed(3)}`}
              />
              <Tooltip 
                formatter={(value, name) => [`$${value.toFixed(4)}`, name]}
                labelStyle={{ color: '#374151' }}
                contentStyle={{ 
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="cost" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                name="Forecasted Cost"
              />
              <Line 
                type="monotone" 
                dataKey="confidence_upper" 
                stroke="#e5e7eb" 
                strokeDasharray="5 5"
                dot={false}
                name="Upper Confidence"
              />
              <Line 
                type="monotone" 
                dataKey="confidence_lower" 
                stroke="#e5e7eb" 
                strokeDasharray="5 5"
                dot={false}
                name="Lower Confidence"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Metrics Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">System Performance</h3>
            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
              perfData?.status === 'healthy' 
                ? 'bg-green-100 text-green-800' 
                : perfData?.status === 'warning'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {perfData?.status || 'Unknown'}
            </span>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">CPU Usage</span>
              <span className="text-sm font-semibold">{perfData?.avg_cpu_usage || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  (perfData?.avg_cpu_usage || 0) > 80 ? 'bg-red-500' :
                  (perfData?.avg_cpu_usage || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${perfData?.avg_cpu_usage || 0}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Memory Usage</span>
              <span className="text-sm font-semibold">{perfData?.avg_memory_usage || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  (perfData?.avg_memory_usage || 0) > 80 ? 'bg-red-500' :
                  (perfData?.avg_memory_usage || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${perfData?.avg_memory_usage || 0}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg Response Time</span>
              <span className="text-sm font-semibold">{perfData?.avg_response_time || 0}ms</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Error Rate</span>
              <span className="text-sm font-semibold">{perfData?.avg_error_rate || 0}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <DollarSign className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Cost optimization applied</p>
                <p className="text-xs text-gray-600">Switched to cost-effective model for routine tasks</p>
              </div>
            </div>
            <span className="text-xs text-gray-500">2 min ago</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <Zap className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Performance improved</p>
                <p className="text-xs text-gray-600">Response time reduced by 15%</p>
              </div>
            </div>
            <span className="text-xs text-gray-500">5 min ago</span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-4 h-4 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Budget alert threshold reached</p>
                <p className="text-xs text-gray-600">80% of hourly budget consumed</p>
              </div>
            </div>
            <span className="text-xs text-gray-500">8 min ago</span>
          </div>
        </div>
      </div>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500">
        Last updated: {lastUpdated.toLocaleTimeString()}
      </div>
    </div>
  );
};

export default Dashboard;
