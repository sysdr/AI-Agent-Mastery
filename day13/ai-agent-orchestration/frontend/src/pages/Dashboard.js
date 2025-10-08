import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import axios from 'axios';

const Dashboard = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSystemStatus();
    fetchMetrics();
    
    // Set up periodic updates
    const interval = setInterval(() => {
      fetchSystemStatus();
      fetchMetrics();
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get('/api/status');
      setSystemStatus(response.data);
    } catch (err) {
      console.error('Failed to fetch system status:', err);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get('/api/metrics');
      setMetrics(response.data);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post('/api/research', {
        query,
        tools: {
          web_search: true,
          fact_checker: true,
          content_synthesizer: true
        },
        security_level: 'standard'
      });
      
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Research failed');
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Advanced Tool Orchestration & Monitoring Dashboard
      </Typography>

      {/* System Status Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                System Status
              </Typography>
              <Typography variant="h5">
                <Chip 
                  label={systemStatus?.status || 'Unknown'} 
                  color={systemStatus?.status === 'healthy' ? 'success' : 'error'}
                />
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Orchestrations
              </Typography>
              <Typography variant="h5">
                {systemStatus?.active_orchestrations || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Cost ($)
              </Typography>
              <Typography variant="h5">
                ${(systemStatus?.total_cost || 0).toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Security Incidents
              </Typography>
              <Typography variant="h5" color={systemStatus?.security_incidents > 0 ? 'error' : 'inherit'}>
                {systemStatus?.security_incidents || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Research Interface */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Research Agent
            </Typography>
            
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Research Query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your research question..."
                multiline
                rows={3}
                sx={{ mb: 2 }}
              />
              
              <Button
                type="submit"
                variant="contained"
                disabled={loading || !query.trim()}
                fullWidth
              >
                {loading ? 'Researching...' : 'Execute Research'}
              </Button>
            </Box>

            {loading && <LinearProgress sx={{ mt: 2 }} />}
            
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error}
              </Alert>
            )}

            {results && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Research Results
                </Typography>
                
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Query: {results.query}
                    </Typography>
                    <Typography variant="body2" paragraph>
                      {results.synthesis?.synthesis || 'Research completed successfully'}
                    </Typography>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2">Sources Used:</Typography>
                      {results.sources?.map((source, index) => (
                        <Chip key={index} label={source} sx={{ mr: 1, mt: 1 }} />
                      ))}
                    </Box>
                    
                    <Box sx={{ mt: 2 }}>
                      <Chip 
                        label={`Security Validated: ${results.security_validated ? 'Yes' : 'No'}`}
                        color={results.security_validated ? 'success' : 'warning'}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Metrics and Monitoring */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Metrics
            </Typography>

            {metrics && (
              <>
                {/* Performance Metrics */}
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Performance Overview
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2">Success Rate</Typography>
                        <Typography variant="h6">{metrics.system_health?.success_rate}%</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">Avg Execution Time</Typography>
                        <Typography variant="h6">{metrics.system_health?.avg_execution_time}s</Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>

                {/* Tool Usage Chart */}
                {metrics.tool_usage && Object.keys(metrics.tool_usage).length > 0 && (
                  <Card sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        Tool Usage Distribution
                      </Typography>
                      <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                          <Pie
                            data={Object.entries(metrics.tool_usage).map(([tool, count]) => ({
                              name: tool,
                              value: count
                            }))}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                          >
                            {Object.keys(metrics.tool_usage).map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}

                {/* Recent Orchestrations */}
                {metrics.recent_orchestrations && (
                  <Card>
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        Recent Orchestrations
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Request ID</TableCell>
                              <TableCell>Status</TableCell>
                              <TableCell>Time (s)</TableCell>
                              <TableCell>Cost ($)</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {metrics.recent_orchestrations.map((row) => (
                              <TableRow key={row.request_id}>
                                <TableCell>{row.request_id.substring(0, 8)}...</TableCell>
                                <TableCell>
                                  <Chip 
                                    label={row.success ? 'Success' : 'Failed'}
                                    color={row.success ? 'success' : 'error'}
                                    size="small"
                                  />
                                </TableCell>
                                <TableCell>{row.execution_time.toFixed(2)}</TableCell>
                                <TableCell>${row.total_cost.toFixed(3)}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
