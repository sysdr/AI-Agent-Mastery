import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import SecurityMonitor from './components/SecurityMonitor';
import ComplianceReport from './components/ComplianceReport';
import Navigation from './components/Navigation';
import { WebSocketProvider } from './hooks/useWebSocket';
import { Toaster } from 'react-hot-toast';
import './App.css';

function App() {
  return (
    <WebSocketProvider>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="app">
          <Navigation />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/security" element={<SecurityMonitor />} />
              <Route path="/compliance" element={<ComplianceReport />} />
            </Routes>
          </main>
          <Toaster position="top-right" />
        </div>
      </Router>
    </WebSocketProvider>
  );
}

export default App;
