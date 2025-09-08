import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Avatar,
  Chip,
  Card,
  CardContent,
  Grid,
  LinearProgress,
} from '@mui/material';
import { Send, SmartToy, Person, Security, Psychology } from '@mui/icons-material';
// Using native WebSocket instead of Socket.IO

const ConversationChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: 'Hello! I\'m your AI engineering mentor. How can I help you learn about distributed systems today?',
      timestamp: new Date(),
      complianceScore: 1.0,
      personalityConsistent: true,
    },
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection using native WebSocket
    const wsUrl = `ws://localhost:8000/ws/${sessionId}`;
    socketRef.current = new WebSocket(wsUrl);

    socketRef.current.onopen = () => {
      setConnectionStatus('connected');
      console.log('WebSocket connected');
    };

    socketRef.current.onclose = () => {
      setConnectionStatus('disconnected');
      console.log('WebSocket disconnected');
    };

    socketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('error');
    };

    socketRef.current.onmessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: 'ai',
          text: response.response,
          timestamp: new Date(),
          complianceScore: response.compliance_score || 1.0,
          personalityConsistent: response.personality_consistent !== false,
          escalated: response.escalated || false,
        }]);
        setIsLoading(false);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        setIsLoading(false);
      }
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: currentMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Send via WebSocket or fallback to HTTP
    if (socketRef.current && connectionStatus === 'connected') {
      socketRef.current.send(JSON.stringify({
        message: currentMessage,
        session_id: sessionId,
        user_id: 'demo_user',
      }));
    } else {
      // HTTP fallback
      try {
        const response = await fetch('http://localhost:8000/api/conversation/process', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: currentMessage,
            session_id: sessionId,
            user_id: 'demo_user',
          }),
        });

        if (response.ok) {
          const data = await response.json();
          setMessages(prev => [...prev, {
            id: Date.now(),
            sender: 'ai',
            text: data.response,
            timestamp: new Date(),
            complianceScore: data.compliance_score || 1.0,
            personalityConsistent: data.personality_consistent !== false,
            escalated: data.escalated || false,
          }]);
        }
      } catch (error) {
        console.error('Message send failed:', error);
        setMessages(prev => [...prev, {
          id: Date.now(),
          sender: 'ai',
          text: 'I\'m experiencing technical difficulties. Please try again.',
          timestamp: new Date(),
          complianceScore: 1.0,
          personalityConsistent: true,
        }]);
      }
      setIsLoading(false);
    }

    setCurrentMessage('');
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const MessageBubble = ({ message }) => {
    const isAI = message.sender === 'ai';
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isAI ? 'flex-start' : 'flex-end',
          mb: 2,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', maxWidth: '70%' }}>
          {isAI && (
            <Avatar sx={{ bgcolor: '#667eea', mr: 1 }}>
              <SmartToy />
            </Avatar>
          )}
          
          <Card
            sx={{
              bgcolor: isAI ? '#f5f5f5' : '#667eea',
              color: isAI ? 'text.primary' : 'white',
              borderRadius: 2,
              ...(isAI ? {} : { ml: 1 }),
            }}
          >
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Typography variant="body1" sx={{ mb: 1 }}>
                {message.text}
              </Typography>
              
              {isAI && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
                  <Chip
                    size="small"
                    icon={<Security />}
                    label={`Compliance: ${(message.complianceScore * 100).toFixed(1)}%`}
                    color={message.complianceScore > 0.8 ? 'success' : 'warning'}
                    variant="outlined"
                  />
                  <Chip
                    size="small"
                    icon={<Psychology />}
                    label={message.personalityConsistent ? 'Consistent' : 'Anomaly'}
                    color={message.personalityConsistent ? 'success' : 'error'}
                    variant="outlined"
                  />
                  {message.escalated && (
                    <Chip
                      size="small"
                      label="Escalated"
                      color="warning"
                      variant="outlined"
                    />
                  )}
                </Box>
              )}
              
              <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
                {message.timestamp.toLocaleTimeString()}
              </Typography>
            </CardContent>
          </Card>
          
          {!isAI && (
            <Avatar sx={{ bgcolor: '#764ba2', ml: 1 }}>
              <Person />
            </Avatar>
          )}
        </Box>
      </Box>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        AI Conversation Interface
      </Typography>

      {/* Connection Status */}
      <Paper elevation={1} sx={{ p: 2, mb: 2, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="body2">
            Connection Status: 
            <Chip
              size="small"
              label={connectionStatus}
              color={connectionStatus === 'connected' ? 'success' : 'error'}
              sx={{ ml: 1 }}
            />
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Session: {sessionId}
          </Typography>
        </Box>
      </Paper>

      {/* Chat Area */}
      <Paper
        elevation={2}
        sx={{
          height: 500,
          display: 'flex',
          flexDirection: 'column',
          borderRadius: 2,
          overflow: 'hidden',
        }}
      >
        {/* Messages */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            p: 2,
            bgcolor: '#fafafa',
          }}
        >
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ bgcolor: '#667eea', mr: 1 }}>
                <SmartToy />
              </Avatar>
              <Paper sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  AI is thinking...
                </Typography>
                <LinearProgress sx={{ mt: 1, borderRadius: 1 }} />
              </Paper>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box sx={{ p: 2, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Ask me about distributed systems, AI agents, or production engineering..."
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              multiline
              maxRows={3}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!currentMessage.trim() || isLoading}
              sx={{
                minWidth: 60,
                borderRadius: 2,
                background: 'linear-gradient(45deg, #667eea, #764ba2)',
              }}
            >
              <Send />
            </Button>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ConversationChat;
