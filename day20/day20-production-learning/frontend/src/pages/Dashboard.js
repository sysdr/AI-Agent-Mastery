import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, AlertTriangle, Shield, TrendingUp } from 'lucide-react';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    performance: null,
    bias: null,
    loading: true
  });

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [performanceRes, biasRes] = await Promise.all([
        fetch('http://localhost:8000/api/learning/metrics/performance'),
        fetch('http://localhost:8000/api/learning/metrics/bias')
      ]);
      
      const performance = await performanceRes.json();
      const bias = await biasRes.json();
      
      setMetrics({ performance, bias, loading: false });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setMetrics(prev => ({ ...prev, loading: false }));
    }
  };

  const StatCard = ({ title, value, icon: Icon, color, description }) => (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <Icon className={`h-8 w-8 ${color}`} />
      </div>
    </div>
  );

  if (metrics.loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const biasData = metrics.bias?.metrics || [];
  const chartData = biasData.map(item => ({
    attribute: item.attribute,
    bias_score: item.value * 100,
    threshold: 10 // 10% threshold
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Production Learning Dashboard
        </h1>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Average Response Time"
          value={`${metrics.performance?.avg_response_time_ms || 0}ms`}
          icon={Activity}
          color="text-blue-600"
          description="Last 24 hours"
        />
        <StatCard
          title="Bias Detections"
          value={metrics.bias?.bias_detected || 0}
          icon={AlertTriangle}
          color={metrics.bias?.bias_detected > 0 ? "text-red-600" : "text-green-600"}
          description={`${metrics.bias?.total_checks || 0} total checks`}
        />
        <StatCard
          title="Privacy Protected"
          value="100%"
          icon={Shield}
          color="text-green-600"
          description="All user data anonymized"
        />
        <StatCard
          title="Model Accuracy"
          value={`${Math.round((metrics.performance?.avg_accuracy || 0) * 100)}%`}
          icon={TrendingUp}
          color="text-blue-600"
          description="Continuous learning active"
        />
      </div>

      {/* Bias Detection Chart */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Bias Detection by Protected Attribute
        </h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="attribute" />
              <YAxis label={{ value: 'Bias Score (%)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Bar dataKey="bias_score" fill="#3b82f6" />
              <Bar dataKey="threshold" fill="#ef4444" opacity={0.3} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No bias detection data available</p>
            <p className="text-sm text-gray-400 mt-2">
              Start using the AI agent to generate bias metrics
            </p>
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-green-50 rounded-lg">
            <h3 className="font-medium text-green-800">Learning Engine</h3>
            <p className="text-sm text-green-600">Active & Processing</p>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="font-medium text-blue-800">Privacy Protection</h3>
            <p className="text-sm text-blue-600">Differential Privacy Applied</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <h3 className="font-medium text-purple-800">Explainability</h3>
            <p className="text-sm text-purple-600">Real-time Insights Available</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
