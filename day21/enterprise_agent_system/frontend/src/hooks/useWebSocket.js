import React, { createContext, useContext, useEffect, useState } from 'react';

const WebSocketContext = createContext();

export const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    // Connect to WebSocket with retry logic
    let newSocket;
    let retryTimeout;
    
    const connect = () => {
      try {
        newSocket = new WebSocket('ws://localhost:8000/ws');
        
        newSocket.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          // Clear any retry timeout
          if (retryTimeout) {
            clearTimeout(retryTimeout);
          }
        };

        newSocket.onclose = (event) => {
          console.log('WebSocket disconnected', event.code, event.reason);
          setIsConnected(false);
          
          // Retry connection after 3 seconds if not manually closed
          if (event.code !== 1000) {
            retryTimeout = setTimeout(() => {
              console.log('Retrying WebSocket connection...');
              connect();
            }, 3000);
          }
        };

        newSocket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);
            setLastMessage(data);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        newSocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
        };

        setSocket(newSocket);
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        setIsConnected(false);
      }
    };

    connect();

    return () => {
      if (retryTimeout) {
        clearTimeout(retryTimeout);
      }
      if (newSocket) {
        newSocket.close(1000, 'Component unmounting');
      }
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ socket, isConnected, lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
