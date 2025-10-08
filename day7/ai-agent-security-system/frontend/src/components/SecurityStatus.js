import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { apiService } from '../services/apiService';

const SecurityStatus = () => {
  const [securityStatus, setSecurityStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSecurityStatus();
  }, []);

  const fetchSecurityStatus = async () => {
    try {
      const data = await apiService.getSecurityStatus();
      setSecurityStatus(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch security status:', error);
      setLoading(false);
    }
  };

  if (loading) return <div className="animate-spin h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>;

  const getThreatLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Security Status</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Status</p>
              <p className="text-2xl font-bold text-green-600">{securityStatus?.status || 'Unknown'}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Agents</p>
              <p className="text-2xl font-bold text-blue-600">{securityStatus?.active_agents || 0}</p>
            </div>
            <Shield className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className={`rounded-lg shadow p-6 ${getThreatLevelColor(securityStatus?.threat_level)}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Threat Level</p>
              <p className="text-2xl font-bold">{securityStatus?.threat_level?.toUpperCase() || 'UNKNOWN'}</p>
            </div>
            <AlertTriangle className="h-8 w-8" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityStatus;
