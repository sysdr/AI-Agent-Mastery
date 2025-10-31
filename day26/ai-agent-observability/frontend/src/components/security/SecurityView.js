import React, { useState, useEffect } from 'react';
import moment from 'moment';
import { securityAPI } from '../../services/api';

const SecurityView = ({ wsData }) => {
  const [alerts, setAlerts] = useState([]);
  const [threatSummary, setThreatSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState('');

  useEffect(() => {
    const fetchSecurityData = async () => {
      try {
        const [alertsData, summaryData] = await Promise.all([
          securityAPI.getAlerts(filterSeverity || null),
          securityAPI.getThreatSummary(24)
        ]);
        setAlerts(alertsData || []);
        setThreatSummary(summaryData);
      } catch (error) {
        console.error('Error fetching security data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 5000);
    return () => clearInterval(interval);
  }, [filterSeverity]);

  useEffect(() => {
    if (wsData?.alerts) {
      setAlerts(wsData.alerts);
    }
  }, [wsData]);

  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-red-600 text-white';
      case 'HIGH':
        return 'bg-orange-500 text-white';
      case 'MEDIUM':
        return 'bg-yellow-500 text-white';
      case 'LOW':
        return 'bg-blue-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading security data...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Security Dashboard</h2>
        <p className="text-gray-600 mb-4">Real-time security monitoring and threat analysis</p>
      </div>

      {/* Threat Summary */}
      {threatSummary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-red-100">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Total Threats</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {threatSummary.total_threats || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-orange-100">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Critical</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {threatSummary.critical_count || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-yellow-100">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">High</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {threatSummary.high_count || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-sm font-medium text-gray-500">Resolved</h3>
                <p className="text-2xl font-bold text-gray-900">
                  {threatSummary.resolved_count || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Filter by Severity:</label>
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <div className="ml-auto text-sm text-gray-500">
            {alerts.length} active alert{alerts.length !== 1 ? 's' : ''}
          </div>
        </div>
      </div>

      {/* Security Alerts */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Security Alerts</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {alerts.length > 0 ? (
            alerts.map((alert, index) => (
              <div
                key={alert.alert_id || index}
                className="p-4 border rounded-lg border-gray-200 hover:border-gray-300 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className={`px-3 py-1 text-xs font-semibold rounded ${getSeverityColor(
                          alert.severity
                        )}`}
                      >
                        {alert.severity || 'UNKNOWN'}
                      </span>
                      <span className="text-sm font-medium text-gray-900">
                        {alert.alert_type || alert.type || 'Security Alert'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">
                      {alert.message || alert.description || 'No description available'}
                    </p>
                    <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                      {alert.timestamp && (
                        <span>
                          {moment(alert.timestamp).format('MMM DD, HH:mm:ss')}
                        </span>
                      )}
                      {alert.source && <span>Source: {alert.source}</span>}
                      {alert.agent_id && <span>Agent: {alert.agent_id}</span>}
                    </div>
                    {alert.metadata && Object.keys(alert.metadata).length > 0 && (
                      <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                        <pre className="whitespace-pre-wrap">
                          {JSON.stringify(alert.metadata, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              {filterSeverity
                ? `No ${filterSeverity.toLowerCase()} alerts`
                : 'No security alerts at this time'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SecurityView;
