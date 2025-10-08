import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import MessageBubble from './MessageBubble';
import FileUpload from './FileUpload';
import SystemMetrics from './SystemMetrics';

const API_BASE = 'http://localhost:8000';
const DEMO_TOKEN = 'demo-token'; // In production, get from auth

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content, file = null) => {
    if (!content.trim() && !file) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: content,
      timestamp: new Date(),
      file: file ? { name: file.name, type: file.type } : null
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      let response;
      
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('message', content);
        
        response = await axios.post(`${API_BASE}/chat/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${DEMO_TOKEN}`
          }
        });
      } else {
        response = await axios.post(`${API_BASE}/chat`, {
          content: content,
          conversation_id: conversationId
        }, {
          headers: {
            'Authorization': `Bearer ${DEMO_TOKEN}`
          }
        });
      }

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.data.content,
        timestamp: new Date(),
        metadata: {
          tokens_used: response.data.tokens_used,
          model_used: response.data.model_used
        }
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.data.conversation_id);
      
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to send message. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  const handleFileUpload = (file, message = '') => {
    sendMessage(message, file);
  };

  return (
    <div className="chat-interface">
      <header className="chat-header">
        <div className="header-content">
          <h1>Multi-Modal Chat Agent</h1>
          <div className="header-actions">
            <a href="/dashboard" className="nav-link">Dashboard</a>
            <a href="/admin" className="nav-link">Admin</a>
          </div>
        </div>
        <SystemMetrics />
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to Multi-Modal Chat</h2>
              <p>Send messages, upload images, PDFs, or Word documents to get started.</p>
            </div>
          )}
          
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="loading-message">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <FileUpload onFileUpload={handleFileUpload} />
          
          <form onSubmit={handleSubmit} className="message-form">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your message..."
              className="message-input"
              disabled={isLoading}
            />
            <button 
              type="submit" 
              disabled={isLoading || !inputText.trim()}
              className="send-button"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
