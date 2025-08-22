import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  Box,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  CircularProgress
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function Dashboard() {
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/status`);
      setStatus(response.data);
      
      // Update metrics for chart
      setMetrics(prev => [...prev.slice(-9), {
        time: new Date().toLocaleTimeString(),
        requests: response.data.request_count || 0
      }]);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  const sendMessage = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: message,
        context: { timestamp: new Date().toISOString() }
      });
      
      setChatHistory(prev => [...prev, {
        type: 'user',
        content: message,
        timestamp: new Date().toLocaleTimeString()
      }, {
        type: 'agent',
        content: response.data.response,
        timestamp: response.data.timestamp
      }]);
      
      setMessage('');
    } catch (error) {
      setChatHistory(prev => [...prev, {
        type: 'error',
        content: 'Failed to send message: ' + error.message,
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Enterprise Agent Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Status Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Status
              </Typography>
              {status ? (
                <Box>
                  <Chip 
                    label={status.health} 
                    color={status.health === 'healthy' ? 'success' : 'error'}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2">
                    Agent ID: {status.agent_id?.substring(0, 8)}...
                  </Typography>
                  <Typography variant="body2">
                    Requests: {status.request_count || 0}
                  </Typography>
                  <Typography variant="body2">
                    Running: {status.is_running ? 'Yes' : 'No'}
                  </Typography>
                </Box>
              ) : (
                <CircularProgress size={24} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Metrics Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Request Metrics
              </Typography>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="requests" stroke="#2196f3" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Chat Interface */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, height: 400, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Chat with Agent
            </Typography>
            
            <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
              <List>
                {chatHistory.map((item, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Chip 
                            size="small" 
                            label={item.type} 
                            color={item.type === 'user' ? 'primary' : item.type === 'agent' ? 'success' : 'error'}
                          />
                          <Typography variant="caption">{item.timestamp}</Typography>
                        </Box>
                      }
                      secondary={item.content}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
            
            <Box display="flex" gap={1}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Type your message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                disabled={loading}
              />
              <Button 
                variant="contained" 
                onClick={sendMessage}
                disabled={loading || !message.trim()}
              >
                {loading ? <CircularProgress size={20} /> : 'Send'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* System Info */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Information
              </Typography>
              {status && (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    <strong>Session:</strong> {status.session_id?.substring(0, 8)}...
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>Last Interaction:</strong> {status.last_interaction ? 
                      new Date(status.last_interaction).toLocaleString() : 'None'}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    <strong>State Keys:</strong> {status.state_keys?.length || 0}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
