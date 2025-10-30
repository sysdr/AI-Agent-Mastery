import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import CostAnalytics from './components/CostAnalytics';
import PerformanceMonitor from './components/PerformanceMonitor';
import Forecasting from './components/Forecasting';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cost-analytics" element={<CostAnalytics />} />
            <Route path="/performance" element={<PerformanceMonitor />} />
            <Route path="/forecasting" element={<Forecasting />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
