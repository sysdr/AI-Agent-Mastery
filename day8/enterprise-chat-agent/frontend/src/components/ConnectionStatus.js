import React from 'react';
import { WifiIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const ConnectionStatus = ({ status, activeConnections = 0 }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'text-green-600';
      case 'connecting':
        return 'text-yellow-600';
      case 'disconnected':
        return 'text-red-600';
      default:
        return 'text-gray-400';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected':
        return 'Connected';
      case 'connecting':
        return 'Connecting...';
      case 'disconnected':
        return 'Disconnected';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="flex items-center space-x-2">
      <div className="flex items-center space-x-1">
        {status === 'connected' ? (
          <WifiIcon className={`h-5 w-5 ${getStatusColor()}`} />
        ) : (
          <ExclamationTriangleIcon className={`h-5 w-5 ${getStatusColor()}`} />
        )}
        <span className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>
      
      {status === 'connected' && (
        <div className="text-sm text-gray-500">
          ({activeConnections} active)
        </div>
      )}
    </div>
  );
};

export default ConnectionStatus;
