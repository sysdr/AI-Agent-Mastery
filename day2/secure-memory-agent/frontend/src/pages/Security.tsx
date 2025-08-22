import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const Security: React.FC = () => {
  const [testText, setTestText] = useState('');
  const [piiResult, setPiiResult] = useState<any>(null);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [securityEvents, setSecurityEvents] = useState<any[]>([]);

  useEffect(() => {
    fetchHealthStatus();
    fetchSecurityEvents();
  }, []);

  const fetchHealthStatus = async () => {
    try {
      const status = await apiService.healthCheck();
      setHealthStatus(status);
    } catch (error) {
      toast.error('Failed to fetch health status');
    }
  };

  const fetchSecurityEvents = async () => {
    try {
      const events = await apiService.getSecurityEvents(20);
      setSecurityEvents(events.events);
    } catch (error) {
      toast.error('Failed to fetch security events');
    }
  };

  const analyzePII = async () => {
    if (!testText.trim()) return;

    try {
      const result = await apiService.analyzePII(testText);
      setPiiResult(result);
      toast.success('PII analysis completed');
    } catch (error) {
      toast.error('PII analysis failed');
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Security Center</h1>

      {/* Health Status */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">System Health</h2>
        {healthStatus && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(healthStatus.checks).map(([check, status]) => (
              <div key={check} className="flex items-center space-x-2">
                {status ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                )}
                <span className="text-sm text-gray-600 capitalize">
                  {check.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* PII Testing */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">PII Detection Test</h2>
        <div className="space-y-4">
          <textarea
            value={testText}
            onChange={(e) => setTestText(e.target.value)}
            placeholder="Enter text to test PII detection (e.g., 'My email is john@example.com and my phone is 555-123-4567')"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            rows={4}
          />
          <button
            onClick={analyzePII}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Analyze PII
          </button>

          {piiResult && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <span className="font-medium">PII Analysis Result</span>
              </div>
              <div className="space-y-2 text-sm">
                <p><strong>PII Detected:</strong> {piiResult.has_pii ? 'Yes' : 'No'}</p>
                <p><strong>Confidence:</strong> {(piiResult.confidence_score * 100).toFixed(1)}%</p>
                {piiResult.has_pii && (
                  <div>
                    <p><strong>Redacted Text:</strong></p>
                    <p className="bg-white p-2 rounded border">{piiResult.redacted_text}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Security Events */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Recent Security Events</h2>
          <button
            onClick={fetchSecurityEvents}
            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
          >
            Refresh
          </button>
        </div>
        <div className="space-y-2">
          {securityEvents.length > 0 ? (
            securityEvents.map((event) => (
              <div key={event.id} className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded">
                <div className="flex items-center space-x-3">
                  <div className={`h-2 w-2 rounded-full ${
                    event.security_level === 'CRITICAL' ? 'bg-red-500' :
                    event.security_level === 'WARNING' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}></div>
                  <span className="text-sm font-medium">{event.event_type}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">No recent security events</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Security;
