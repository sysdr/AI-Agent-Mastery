import React from 'react';
import { NavLink } from 'react-router-dom';

const Navigation = ({ connectionStatus }) => {
  const navItems = [
    { to: '/', label: 'Dashboard' },
    { to: '/traces', label: 'Traces' },
    { to: '/metrics', label: 'Metrics' },
    { to: '/logs', label: 'Logs' },
    { to: '/security', label: 'Security' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Connected': return 'text-green-600';
      case 'Connecting...': return 'text-yellow-600';
      case 'Disconnected': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900">AI Agent Observability</h1>
            </div>
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </div>
          </div>
          <div className="flex items-center">
            <span className="text-sm text-gray-500 mr-2">WebSocket:</span>
            <span className={`text-sm font-medium ${getStatusColor(connectionStatus)}`}>
              {connectionStatus}
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
