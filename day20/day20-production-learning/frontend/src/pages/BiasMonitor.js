import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

const BiasMonitor = () => {
  const [biasData, setBiasData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBiasData();
    const interval = setInterval(fetchBiasData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchBiasData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/learning/metrics/bias');
      const data = await response.json();
      setBiasData(data);
    } catch (error) {
      console.error('Failed to fetch bias data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const metrics = biasData?.metrics || [];
  const biasDetected = biasData?.bias_detected || 0;
  const totalChecks = biasData?.total_checks || 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Bias Detection Monitor</h1>
        <button
          onClick={fetchBiasData}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <RefreshCw size={16} className="inline mr-2" />
          Refresh
        </button>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            {biasDetected === 0 ? (
              <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
            ) : (
              <AlertTriangle className="h-8 w-8 text-red-500 mr-3" />
            )}
            <div>
              <p className="text-sm font-medium text-gray-600">Bias Status</p>
              <p className={`text-2xl font-bold ${
                biasDetected === 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {biasDetected === 0 ? 'No Bias Detected' : `${biasDetected} Issues Found`}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-sm font-medium text-gray-600">Total Checks</p>
          <p className="text-2xl font-bold text-blue-600">{totalChecks}</p>
          <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-sm font-medium text-gray-600">Fairness Score</p>
          <p className="text-2xl font-bold text-green-600">
            {totalChecks > 0 ? Math.round(((totalChecks - biasDetected) / totalChecks) * 100) : 100}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Across all attributes</p>
        </div>
      </div>

      {/* Bias Metrics Details */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Protected Attribute Analysis
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Monitoring fairness across demographic groups
          </p>
        </div>

        <div className="p-6">
          {metrics.length > 0 ? (
            <div className="space-y-4">
              {metrics.map((metric, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {metric.attribute} - {metric.metric_type}
                      </h3>
                      <p className="text-sm text-gray-500">
                        Measured: {new Date(metric.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className={`text-lg font-semibold ${
                        metric.threshold_exceeded ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {(metric.value * 100).toFixed(1)}%
                      </p>
                      <p className="text-xs text-gray-500">
                        Threshold: 10%
                      </p>
                    </div>
                  </div>
                  
                  {metric.threshold_exceeded && (
                    <div className="mt-3 p-3 bg-red-50 rounded-md">
                      <p className="text-sm text-red-800">
                        ⚠️ Bias threshold exceeded! Review model behavior for {metric.attribute}.
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No bias metrics available</p>
              <p className="text-sm text-gray-400 mt-2">
                Use the AI agent to generate data for bias analysis
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Fairness Explanation */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          About Fairness Monitoring
        </h3>
        <p className="text-blue-800 text-sm">
          Our system continuously monitors for bias across protected attributes like age, gender, 
          and location. We use demographic parity and equalized odds metrics to ensure fair 
          treatment across all user groups. Any bias detection triggers automatic alerts and 
          model adjustments.
        </p>
      </div>
    </div>
  );
};

export default BiasMonitor;
