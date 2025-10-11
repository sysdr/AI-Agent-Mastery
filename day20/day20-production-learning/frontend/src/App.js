import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ChatInterface from './pages/ChatInterface';
import BiasMonitor from './pages/BiasMonitor';
import PerformanceAnalytics from './pages/PerformanceAnalytics';
import './App.css';

function App() {
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    // Check backend health
    fetch('http://localhost:8000/api/learning/health')
      .then(res => res.json())
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex items-center space-x-8">
                <h1 className="text-xl font-bold text-gray-800">
                  Production Learning System
                </h1>
                <div className="hidden md:flex space-x-4">
                  <Link 
                    to="/" 
                    className="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md"
                  >
                    Dashboard
                  </Link>
                  <Link 
                    to="/chat" 
                    className="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md"
                  >
                    AI Agent
                  </Link>
                  <Link 
                    to="/bias" 
                    className="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md"
                  >
                    Bias Monitor
                  </Link>
                  <Link 
                    to="/analytics" 
                    className="text-gray-600 hover:text-blue-600 px-3 py-2 rounded-md"
                  >
                    Analytics
                  </Link>
                </div>
              </div>
              <div className="flex items-center">
                <div className={`px-3 py-1 rounded-full text-sm ${
                  isHealthy 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {isHealthy ? '● Healthy' : '● Offline'}
                </div>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto py-6 px-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<ChatInterface />} />
            <Route path="/bias" element={<BiasMonitor />} />
            <Route path="/analytics" element={<PerformanceAnalytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
