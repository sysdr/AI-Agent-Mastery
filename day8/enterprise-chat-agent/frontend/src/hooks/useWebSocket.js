import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAuth } from './useAuth';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [activeConnections, setActiveConnections] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);
  const connectionId = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    if (isAuthenticated && user) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, user]);

  const connect = () => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    connectionId.current = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const token = localStorage.getItem('access_token');
    const wsUrl = `ws://localhost:8000/ws/${connectionId.current}?token=${encodeURIComponent(token)}`;
    
    try {
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setConnectionStatus('connected');
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        // Start heartbeat
        startHeartbeat();
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setConnectionStatus('disconnected');
        setIsConnected(false);
        
        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, Math.pow(2, reconnectAttempts.current) * 1000); // Exponential backoff
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('disconnected');
        setIsConnected(false);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('disconnected');
      setIsConnected(false);
    }
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close(1000);
      ws.current = null;
    }
    setConnectionStatus('disconnected');
    setIsConnected(false);
  };

  const startHeartbeat = () => {
    const heartbeatInterval = setInterval(() => {
      if (ws.current?.readyState === WebSocket.OPEN) {
        sendMessage({
          type: 'heartbeat',
          timestamp: new Date().toISOString()
        });
      } else {
        clearInterval(heartbeatInterval);
      }
    }, 30000); // Send heartbeat every 30 seconds
  };

  const sendMessage = async (message) => {
    return new Promise((resolve, reject) => {
      if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket not connected'));
        return;
      }

      try {
        const messageWithTenant = {
          ...message,
          tenant_id: user?.tenant_id,
          timestamp: message.timestamp || new Date().toISOString()
        };

        ws.current.send(JSON.stringify(messageWithTenant));
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  };

  const handleMessage = (data) => {
    switch (data.type) {
      case 'heartbeat_ack':
        // Heartbeat acknowledged
        break;
      
      case 'chat_response':
        // Handle AI response - this would be handled by components
        window.dispatchEvent(new CustomEvent('websocket_message', { detail: data }));
        break;
      
      case 'context_sync':
        // Handle context synchronization
        window.dispatchEvent(new CustomEvent('websocket_message', { detail: data }));
        break;
      
      case 'context_updated':
        // Handle context updates from other connections
        window.dispatchEvent(new CustomEvent('websocket_message', { detail: data }));
        break;
      
      case 'quota_exceeded':
        console.warn('Quota exceeded:', data.message);
        window.dispatchEvent(new CustomEvent('quota_exceeded', { detail: data }));
        break;
      
      case 'error':
        console.error('WebSocket error:', data.message);
        break;
      
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const value = {
    connectionStatus,
    activeConnections,
    isConnected,
    sendMessage,
    connect,
    disconnect
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};
