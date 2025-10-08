import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MessageInterface = ({ currentAgent }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState({ receiver_id: '', content: '', type: 'text' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000); // Check for new messages every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMessages = async () => {
    try {
      const response = await axios.get('http://localhost:8000/messages/receive');
      if (response.data.status === 'success') {
        setMessages(prev => [...response.data.messages, ...prev]);
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/message/send', newMessage);
      
      if (response.data.status === 'success') {
        setNewMessage({ receiver_id: '', content: '', type: 'text' });
        
        // Add sent message to display
        const sentMessage = {
          id: response.data.message_id,
          sender_id: currentAgent,
          receiver_id: newMessage.receiver_id,
          content: newMessage.content,
          timestamp: new Date().toISOString(),
          threat_score: response.data.threat_score,
          direction: 'sent'
        };
        setMessages(prev => [sentMessage, ...prev]);
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const getThreatColor = (score) => {
    if (score > 0.7) return '#ff4444';
    if (score > 0.3) return '#ff9944';
    return '#44ff44';
  };

  return (
    <div className="message-interface">
      <h2>💬 Secure Agent Communication</h2>
      
      <div className="message-container">
        <div className="compose-message">
          <h3>Send Encrypted Message</h3>
          <form onSubmit={sendMessage}>
            <div className="form-group">
              <label>To Agent:</label>
              <input
                type="text"
                value={newMessage.receiver_id}
                onChange={(e) => setNewMessage({...newMessage, receiver_id: e.target.value})}
                placeholder="agent-002"
                required
              />
            </div>
            
            <div className="form-group">
              <label>Message Type:</label>
              <select
                value={newMessage.type}
                onChange={(e) => setNewMessage({...newMessage, type: e.target.value})}
              >
                <option value="text">Text</option>
                <option value="command">Command</option>
                <option value="data">Data</option>
                <option value="alert">Alert</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Content:</label>
              <textarea
                value={newMessage.content}
                onChange={(e) => setNewMessage({...newMessage, content: e.target.value})}
                placeholder="Enter your secure message..."
                rows="4"
                required
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button type="submit" disabled={loading} className="send-btn">
              {loading ? 'Encrypting & Sending...' : '🔐 Send Encrypted'}
            </button>
          </form>
        </div>

        <div className="messages-list">
          <h3>Message History</h3>
          <div className="messages">
            {messages.length === 0 ? (
              <p>No messages yet. Send your first encrypted message!</p>
            ) : (
              messages.map((message, index) => (
                <div key={index} className={`message ${message.direction || 'received'}`}>
                  <div className="message-header">
                    <span className="message-route">
                      {message.sender_id} → {message.receiver_id}
                    </span>
                    <span className="message-time">
                      {new Date(message.timestamp).toLocaleString()}
                    </span>
                    {message.threat_score && (
                      <span 
                        className="threat-score"
                        style={{ color: getThreatColor(message.threat_score) }}
                      >
                        Risk: {(message.threat_score * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                  <div className="message-content">
                    <strong>Type:</strong> {message.type || 'text'}<br/>
                    <strong>Content:</strong> {message.content}
                  </div>
                  <div className="message-footer">
                    <span className="encryption-badge">🔐 AES-256 Encrypted</span>
                    <span className="message-id">ID: {message.id}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageInterface;
