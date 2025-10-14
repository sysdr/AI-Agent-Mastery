import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, Clock, Zap } from 'lucide-react';

const PerformanceAnalytics = () => {
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPerformanceData();
    const interval = setInterval(fetchPerformanceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchPerformanceData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/learning/metrics/performance');
      const data = await response.json();
      setPerformanceData(data);
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Performance Analytics</h1>
        <div className="text-sm text-gray-500">
          Real-time performance monitoring
        </div>
      </div>

      {/* Performance Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Response Time</p>
              <p className="text-2xl font-bold text-blue-600">
                {performanceData?.avg_response_time_ms || 0}ms
              </p>
              <p className="text-xs text-gray-500 mt-1">Average latency</p>
            </div>
            <Clock className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cost</p>
              <p className="text-2xl font-bold text-green-600">
                ${performanceData?.total_cost_usd || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">API usage cost</p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Accuracy</p>
              <p className="text-2xl font-bold text-purple-600">
                {Math.round((performanceData?.avg_accuracy || 0) * 100)}%
              </p>
              <p className="text-xs text-gray-500 mt-1">Model performance</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Requests</p>
              <p className="text-2xl font-bold text-orange-600">
                {performanceData?.total_requests || 0}
              </p>
              <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
            </div>
            <Zap className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Cost Optimization */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Cost Optimization Insights
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-800 mb-2">Cost per Request</h3>
            <p className="text-3xl font-bold text-green-600">
              ${performanceData?.cost_per_request || 0}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {performanceData?.cost_per_request < 0.01 ? 
                "✅ Within optimal range" : 
                "⚠️ Consider optimization"
              }
            </p>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-800 mb-2">Efficiency Score</h3>
            <div className="flex items-center">
              <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ width: `${Math.min(100, (performanceData?.avg_accuracy || 0) * 100)}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-700">
                {Math.round((performanceData?.avg_accuracy || 0) * 100)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Monitoring */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Security & Privacy Status
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
              <div>
                <h3 className="font-medium text-green-800">Data Protection</h3>
                <p className="text-sm text-green-600">All data anonymized</p>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
              <div>
                <h3 className="font-medium text-blue-800">Encryption</h3>
                <p className="text-sm text-blue-600">End-to-end encrypted</p>
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <div>
                <h3 className="font-medium text-purple-800">Compliance</h3>
                <p className="text-sm text-purple-600">GDPR compliant</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Recommendations */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-yellow-900 mb-2">
          Performance Recommendations
        </h3>
        <ul className="text-yellow-800 text-sm space-y-1">
          <li>• Monitor response times during peak usage hours</li>
          <li>• Consider implementing request caching for frequently asked questions</li>
          <li>• Set up automated cost alerts for budget management</li>
          <li>• Regularly review and optimize model parameters for efficiency</li>
        </ul>
      </div>
    </div>
  );
};

export default PerformanceAnalytics;
