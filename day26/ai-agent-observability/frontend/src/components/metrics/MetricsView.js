import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import moment from 'moment';
import { metricsAPI } from '../../services/api';

const MetricsView = ({ wsData }) => {
  const [metrics, setMetrics] = useState({
    confidence_metrics: { average: 0, min: 0, max: 0, count: 0 },
    token_metrics: { total_tokens: 0, total_cost: 0, operations_count: 0 },
    anomalies_detected: []
  });
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await metricsAPI.getRealtime();
        setMetrics(data);
        // Add to history for trend visualization
        setHistory(prev => {
          const newHistory = [...prev, {
            time: moment().format('HH:mm:ss'),
            confidence: data.confidence_metrics.average,
            tokens: data.token_metrics.total_tokens,
            cost: data.token_metrics.total_cost
          }];
          // Keep only last 20 data points
          return newHistory.slice(-20);
        });
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (wsData?.metrics) {
      setMetrics(wsData.metrics);
    }
  }, [wsData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading metrics...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Metrics Dashboard</h2>
        <p className="text-gray-600 mb-4">Detailed metrics and performance monitoring</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500">Average Confidence</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {((metrics.confidence_metrics?.average || 0) * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {metrics.confidence_metrics?.count || 0} samples
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500">Total Tokens</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {metrics.token_metrics?.total_tokens?.toLocaleString() || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {metrics.token_metrics?.operations_count || 0} operations
          </p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500">Total Cost</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            ${(metrics.token_metrics?.total_cost || 0).toFixed(3)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Estimated cost</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-sm font-medium text-gray-500">Anomalies</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">
            {metrics.anomalies_detected?.length || 0}
          </p>
          <p className="text-xs text-gray-500 mt-1">Detected</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Confidence Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis domain={[0, 1]} />
              <Tooltip formatter={(value) => [`${(value * 100).toFixed(1)}%`, 'Confidence']} />
              <Legend />
              <Line type="monotone" dataKey="confidence" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Usage</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={history}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="tokens" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Anomalies */}
      {metrics.anomalies_detected && metrics.anomalies_detected.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Detected Anomalies</h3>
          <div className="space-y-3">
            {metrics.anomalies_detected.map((anomaly, index) => (
              <div key={index} className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{anomaly.type}</p>
                    {anomaly.agent_id && (
                      <p className="text-sm text-gray-600">Agent: {anomaly.agent_id}</p>
                    )}
                    {anomaly.timestamp && (
                      <p className="text-xs text-gray-500 mt-1">
                        {moment(anomaly.timestamp).format('MMM DD, HH:mm:ss')}
                      </p>
                    )}
                  </div>
                </div>
                {anomaly.analysis && (
                  <div className="mt-2 text-sm text-gray-700">
                    <pre className="whitespace-pre-wrap">
                      {JSON.stringify(anomaly.analysis, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Metrics JSON */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Raw Metrics Data</h3>
        <pre className="bg-gray-50 p-4 rounded text-xs overflow-auto">
          {JSON.stringify(metrics, null, 2)}
        </pre>
      </div>
    </div>
  );
};

export default MetricsView;
