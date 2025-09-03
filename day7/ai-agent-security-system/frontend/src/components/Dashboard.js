import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer
} from 'recharts';
import { Shield, Activity, AlertTriangle, CheckCircle, Clock, Users } from 'lucide-react';
import { apiService } from '../services/apiService';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await apiService.getDashboardData();
      setDashboardData(data);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      toast.error('Failed to fetch dashboard data');
      setLoading(false);
    }
  };

  const triggerSecurityScan = async () => {
    try {
      const result = await apiService.runSecurityScan();
      toast.success(`Security scan initiated: ${result.scan_id}`);
      setTimeout(fetchDashboardData, 5000); // Refresh after 5 seconds
    } catch (error) {
      toast.error('Failed to start security scan');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="mx-auto h-12 w-12 text-yellow-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">No Data Available</h2>
        <p className="text-gray-600">Unable to load dashboard data</p>
      </div>
    );
  }

  const { security, performance, recent_events, vulnerabilities } = dashboardData;

  // Process performance data for charts
  const performanceHistory = performance?.history?.slice(-20).map((item, index) => ({
    time: index,
    cpu: item.system?.cpu_percent || 0,
    memory: item.system?.memory_percent || 0,
    responseTime: item.performance?.response_time_ms || 0
  })) || [];

  const securityMetrics = [
    {
      title: 'Active Agents',
      value: security?.active_agents || 0,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Health Score',
      value: `${performance?.health_score || 0}%`,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Vulnerabilities',
      value: vulnerabilities?.total_vulnerabilities || 0,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      title: 'Threat Level',
      value: security?.threat_level?.toUpperCase() || 'UNKNOWN',
      icon: Shield,
      color: security?.threat_level === 'high' ? 'text-red-600' : 'text-green-600',
      bgColor: security?.threat_level === 'high' ? 'bg-red-50' : 'bg-green-50'
    }
  ];

  const vulnerabilityData = [
    { name: 'High', value: vulnerabilities?.severity_breakdown?.high || 0, color: '#dc2626' },
    { name: 'Medium', value: vulnerabilities?.severity_breakdown?.medium || 0, color: '#ea580c' },
    { name: 'Low', value: vulnerabilities?.severity_breakdown?.low || 0, color: '#ca8a04' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Assessment Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Real-time monitoring and security assessment for AI Agent systems
          </p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={triggerSecurityScan}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
          >
            <Shield className="h-4 w-4" />
            <span>Run Security Scan</span>
          </button>
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="h-4 w-4 mr-1" />
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {securityMetrics.map((metric, index) => (
          <div key={index} className={`${metric.bgColor} rounded-lg p-6`}>
            <div className="flex items-center">
              <metric.icon className={`h-8 w-8 ${metric.color}`} />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{metric.title}</p>
                <p className={`text-2xl font-bold ${metric.color}`}>{metric.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="cpu" stroke="#3b82f6" strokeWidth={2} name="CPU %" />
              <Line type="monotone" dataKey="memory" stroke="#10b981" strokeWidth={2} name="Memory %" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Vulnerability Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Vulnerability Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={vulnerabilityData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                label={({ name, value }) => value > 0 ? `${name}: ${value}` : ''}
              >
                {vulnerabilityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Security Events</h3>
        </div>
        <div className="p-6">
          {recent_events && recent_events.length > 0 ? (
            <div className="space-y-3">
              {recent_events.slice(0, 5).map((event, index) => (
                <div key={index} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      event.event_type === 'security_scan_initiated' ? 'bg-blue-500' :
                      event.event_type === 'agent_registration' ? 'bg-green-500' :
                      event.event_type === 'auth_failure' ? 'bg-red-500' : 'bg-gray-500'
                    }`}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{event.event_type}</p>
                      <p className="text-xs text-gray-500">Agent: {event.agent_id || 'system'}</p>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No recent events</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
