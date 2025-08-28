import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  TextField,
  Chip,
  Alert
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import MonitoringPanel from '../components/MonitoringPanel';
import CircuitBreakerStatus from '../components/CircuitBreakerStatus';
import RateLimitStatus from '../components/RateLimitStatus';

function Dashboard() {
  const [monitoringData, setMonitoringData] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [newUrl, setNewUrl] = useState('');

  useEffect(() => {
    fetchSystemStatus();
    const interval = setInterval(fetchSystemStatus, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/api/v1/monitoring/status');
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const addMonitoring = async () => {
    if (!newUrl) return;
    
    try {
      const response = await fetch('/api/v1/monitoring/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls: [newUrl],
          name: 'Manual Monitor'
        })
      });
      
      const result = await response.json();
      setMonitoringData(prev => [...prev, ...result.results]);
      setNewUrl('');
    } catch (error) {
      console.error('Failed to add monitoring:', error);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Resilient Agent Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* System Status Overview */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Chip 
                label={systemStatus.status || 'Unknown'} 
                color={systemStatus.status === 'operational' ? 'success' : 'warning'}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Active Domains */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Monitored Domains
              </Typography>
              <Typography variant="h4">
                {systemStatus.active_domains?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Circuit Breaker Status */}
        <Grid item xs={12} md={12} lg={6}>
          <CircuitBreakerStatus data={systemStatus.circuit_breakers || {}} />
        </Grid>

        {/* Add New URL */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Add Product URL
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                label="Product URL"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://example.com/product/123"
              />
              <Button 
                variant="contained" 
                onClick={addMonitoring}
                disabled={!newUrl}
              >
                Monitor
              </Button>
            </Box>
          </Paper>
        </Grid>

        {/* Monitoring Results */}
        <Grid item xs={12}>
          <MonitoringPanel data={monitoringData} />
        </Grid>

        {/* Rate Limiting Status */}
        <Grid item xs={12}>
          <RateLimitStatus />
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
