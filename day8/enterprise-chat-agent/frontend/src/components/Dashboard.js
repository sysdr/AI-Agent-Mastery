import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import ChatInterface from './ChatInterface';
import TenantInfo from './TenantInfo';
import ConnectionStatus from './ConnectionStatus';
import { useAuth } from '../hooks/useAuth';
import { useWebSocket } from '../hooks/useWebSocket';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const { connectionStatus, activeConnections } = useWebSocket();
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [conversations, setConversations] = useState([]);

  useEffect(() => {
    // Initialize with a default conversation
    if (conversations.length === 0) {
      const defaultConversation = {
        id: `conv_${Date.now()}`,
        title: 'New Conversation',
        messages: [],
        created_at: new Date().toISOString()
      };
      setConversations([defaultConversation]);
      setSelectedConversation(defaultConversation.id);
    }
  }, [conversations.length]);

  const createNewConversation = () => {
    const newConversation = {
      id: `conv_${Date.now()}`,
      title: 'New Conversation',
      messages: [],
      created_at: new Date().toISOString()
    };
    setConversations(prev => [newConversation, ...prev]);
    setSelectedConversation(newConversation.id);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar 
        conversations={conversations}
        selectedConversation={selectedConversation}
        onSelectConversation={setSelectedConversation}
        onNewConversation={createNewConversation}
        user={user}
        onLogout={logout}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-semibold text-gray-900">
                Enterprise Chat Agent
              </h1>
              <ConnectionStatus 
                status={connectionStatus}
                activeConnections={activeConnections}
              />
            </div>
            
            <div className="flex items-center space-x-4">
              <TenantInfo user={user} />
            </div>
          </div>
        </header>

        {/* Chat Interface */}
        <main className="flex-1 overflow-hidden">
          <Routes>
            <Route 
              path="/" 
              element={
                <ChatInterface 
                  conversationId={selectedConversation}
                  conversations={conversations}
                  onUpdateConversations={setConversations}
                />
              } 
            />
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
