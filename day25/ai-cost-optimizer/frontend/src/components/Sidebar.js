import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  DollarSign, 
  Activity, 
  TrendingUp,
  Settings,
  Zap
} from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Cost Analytics', href: '/cost-analytics', icon: DollarSign },
    { name: 'Performance', href: '/performance', icon: Activity },
    { name: 'Forecasting', href: '/forecasting', icon: TrendingUp },
  ];

  const isActive = (href) => location.pathname === href;

  return (
    <div className="bg-white w-64 shadow-sm border-r border-gray-200 flex flex-col">
      {/* Logo/Brand */}
      <div className="flex items-center px-6 py-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">AI Cost Optimizer</h1>
            <p className="text-xs text-gray-600">v1.0.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                isActive(item.href)
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon
                className={`mr-3 h-5 w-5 flex-shrink-0 ${
                  isActive(item.href)
                    ? 'text-blue-600'
                    : 'text-gray-400 group-hover:text-gray-600'
                }`}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="px-4 py-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 px-3 py-2">
          <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
            <Settings className="w-4 h-4 text-gray-600" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">Settings</p>
            <p className="text-xs text-gray-600">Configure optimization</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
