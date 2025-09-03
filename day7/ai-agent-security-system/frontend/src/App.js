import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Dashboard from './components/Dashboard';
import SecurityStatus from './components/SecurityStatus';
import AuditLog from './components/AuditLog';
import VulnerabilityReport from './components/VulnerabilityReport';
import Navbar from './components/Navbar';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/security" element={<SecurityStatus />} />
            <Route path="/audit" element={<AuditLog />} />
            <Route path="/vulnerabilities" element={<VulnerabilityReport />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;
