import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/dashboard/Dashboard';
import TracesView from './components/traces/TracesView';
import MetricsView from './components/metrics/MetricsView';
import LogsView from './components/logs/LogsView';
import SecurityView from './components/security/SecurityView';
import Navigation from './components/Navigation';
import './App.css';

function App() {
  const [wsData, setWsData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Connecting...');

  useEffect(() => {
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000;

    const connectWebSocket = () => {
      try {
        // In development with proxy, use relative URL
        // Otherwise use explicit WebSocket URL
        const useProxy = !process.env.REACT_APP_WS_URL;
        const wsUrl = useProxy 
          ? `ws://localhost:8000/ws`
          : `${process.env.REACT_APP_WS_URL}/ws`;
        
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
          setConnectionStatus('Connected');
          reconnectAttempts = 0;
          console.log('WebSocket connected');
        };
        
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setWsData(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };
        
        ws.onclose = (event) => {
          if (!event.wasClean && reconnectAttempts < maxReconnectAttempts) {
            setConnectionStatus('Reconnecting...');
            reconnectAttempts++;
            setTimeout(connectWebSocket, reconnectDelay);
          } else {
            setConnectionStatus('Disconnected');
            console.log('WebSocket disconnected');
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          // Don't update status on error, let onclose handle it
        };
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        setConnectionStatus('WebSocket unavailable');
      }
    };

    connectWebSocket();
    
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation connectionStatus={connectionStatus} />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard wsData={wsData} />} />
            <Route path="/traces" element={<TracesView wsData={wsData} />} />
            <Route path="/metrics" element={<MetricsView wsData={wsData} />} />
            <Route path="/logs" element={<LogsView wsData={wsData} />} />
            <Route path="/security" element={<SecurityView wsData={wsData} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
