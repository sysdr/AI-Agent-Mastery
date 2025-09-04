import React, { useState, useEffect, useRef } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-toastify';
import { useWebSocket } from '../hooks/useWebSocket';
import MessageBubble from './MessageBubble';

const ChatInterface = ({ conversationId, conversations, onUpdateConversations }) => {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { sendMessage, isConnected } = useWebSocket();

  const currentConversation = conversations.find(c => c.id === conversationId);
  const messages = currentConversation?.messages || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!message.trim() || !isConnected) {
      return;
    }

    const userMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    updateConversationMessages([...messages, userMessage]);
    setMessage('');
    setIsTyping(true);

    try {
      // Send message via WebSocket
      await sendMessage({
        type: 'chat_message',
        conversation_id: conversationId,
        content: userMessage.content,
        timestamp: userMessage.timestamp
      });

    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
      setIsTyping(false);
    }
  };

  const updateConversationMessages = (newMessages) => {
    onUpdateConversations(prevConversations => 
      prevConversations.map(conv => 
        conv.id === conversationId 
          ? { ...conv, messages: newMessages }
          : conv
      )
    );
  };

  // Listen for incoming messages
  useEffect(() => {
    const handleMessage = (data) => {
      if (data.type === 'chat_response' && data.conversation_id === conversationId) {
        const aiMessage = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: data.content,
          timestamp: data.timestamp
        };
        
        updateConversationMessages([...messages, aiMessage]);
        setIsTyping(false);
      }
    };

    // In a real implementation, this would be handled by the WebSocket hook
    // For now, simulate AI responses
    if (isTyping) {
      const timer = setTimeout(() => {
        const aiMessage = {
          id: `msg_${Date.now()}`,
          role: 'assistant',
          content: `I understand you said: "${messages[messages.length - 1]?.content}". As an enterprise AI assistant, I'm here to help with your inquiries. Please note that this is a demo implementation showcasing multi-tenant architecture with real-time synchronization.`,
          timestamp: new Date().toISOString()
        };
        
        updateConversationMessages([...messages, aiMessage]);
        setIsTyping(false);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [isTyping, conversationId, messages, updateConversationMessages]);

  if (!conversationId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <p className="text-gray-500">Select a conversation to start chatting</p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-8">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-500">
              Ask me anything! I'm your enterprise AI assistant.
            </p>
          </div>
        )}
        
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        
        {isTyping && (
          <div className="flex items-center space-x-2">
            <div className="bg-white rounded-lg px-4 py-2 shadow">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <form onSubmit={handleSendMessage} className="flex space-x-4">
          <div className="flex-1">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={isConnected ? "Type your message..." : "Connecting..."}
              disabled={!isConnected}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100"
            />
          </div>
          <button
            type="submit"
            disabled={!message.trim() || !isConnected || isTyping}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </form>
        
        {!isConnected && (
          <p className="text-red-500 text-sm mt-2">
            Connection lost. Attempting to reconnect...
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
