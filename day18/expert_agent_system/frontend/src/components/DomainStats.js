import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, CheckCircle, Database } from 'lucide-react';

const DomainStats = ({ domain }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (domain) {
      fetchDomainStats(domain);
    }
  }, [domain]);

  const fetchDomainStats = async (domainName) => {
    setLoading(true);
    try {
      const response = await fetch(`/stats/${domainName}`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch domain stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-1/2 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-300 rounded"></div>
            <div className="h-8 bg-gray-300 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center mb-4">
        <BarChart3 className="text-green-600 mr-2" size={20} />
        <h3 className="text-lg font-semibold">Domain Statistics</h3>
      </div>

      <div className="space-y-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total Entries</span>
            <Database className="text-gray-500" size={16} />
          </div>
          <div className="text-2xl font-bold text-gray-900">{stats.total_entries}</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Validated</span>
            <CheckCircle className="text-green-500" size={16} />
          </div>
          <div className="flex items-end justify-between">
            <div className="text-2xl font-bold text-gray-900">{stats.validated_entries}</div>
            <div className="text-sm text-green-600 font-medium">
              {(stats.validation_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              className="bg-green-500 h-2 rounded-full" 
              style={{ width: `${stats.validation_rate * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Avg Confidence</span>
            <TrendingUp className="text-blue-500" size={16} />
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {(stats.average_confidence * 100).toFixed(1)}%
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
            <div 
              className="bg-blue-500 h-2 rounded-full" 
              style={{ width: `${stats.average_confidence * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="text-center">
          <div className="text-xs text-gray-500 capitalize">
            Domain: {stats.domain}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DomainStats;
