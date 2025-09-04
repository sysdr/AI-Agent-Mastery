import React, { useState, useEffect } from 'react';
import { BuildingOfficeIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

const TenantInfo = ({ user }) => {
  const [tenantInfo, setTenantInfo] = useState(null);
  const [quotaInfo, setQuotaInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTenantInfo();
  }, []);

  const fetchTenantInfo = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('/tenant/info', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setTenantInfo(response.data.tenant_info);
      setQuotaInfo(response.data.quota_info);
    } catch (error) {
      console.error('Failed to fetch tenant info:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
        <span className="text-sm text-gray-500">Loading...</span>
      </div>
    );
  }

  const quotaPercentage = quotaInfo ? 
    (quotaInfo.daily_messages_used / quotaInfo.daily_message_limit) * 100 : 0;

  return (
    <div className="flex items-center space-x-4">
      <div className="flex items-center space-x-2">
        <BuildingOfficeIcon className="h-5 w-5 text-gray-400" />
        <div>
          <p className="text-sm font-medium text-gray-900">
            {tenantInfo?.name || 'Unknown Tenant'}
          </p>
          <p className="text-xs text-gray-500">
            {tenantInfo?.domain || user?.tenant_id}
          </p>
        </div>
      </div>

      {quotaInfo && (
        <div className="flex items-center space-x-2">
          <ChartBarIcon className="h-5 w-5 text-gray-400" />
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">
              {quotaInfo.current_connections}/{quotaInfo.max_connections}
            </p>
            <div className="flex items-center space-x-1">
              <div className="w-16 bg-gray-200 rounded-full h-1.5">
                <div 
                  className="bg-indigo-600 h-1.5 rounded-full quota-bar"
                  style={{ width: `${Math.min(quotaPercentage, 100)}%` }}
                ></div>
              </div>
              <span className="text-xs text-gray-500">
                {quotaInfo.daily_messages_used}/{quotaInfo.daily_message_limit}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TenantInfo;
