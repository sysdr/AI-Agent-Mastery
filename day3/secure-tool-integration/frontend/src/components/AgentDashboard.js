import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Card,
  CardContent,
  Box,
  Chip
} from '@mui/material';
import { PlayArrow, Security, Build } from '@mui/icons-material';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css';
import ApiService from '../services/ApiService';

function AgentDashboard() {
  const [command, setCommand] = useState('');
  const [parameters, setParameters] = useState('{"path": "/home/user/documents"}');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [capabilities, setCapabilities] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCapabilities();
  }, []);

  const loadCapabilities = async () => {
    try {
      const response = await ApiService.getCapabilities();
      setCapabilities(response.capabilities);
    } catch (err) {
      setError('Failed to load capabilities');
    }
  };

  const executeCommand = async () => {
    setLoading(true);
    setError('');
    try {
      const params = JSON.parse(parameters);
      const response = await ApiService.executeCommand(command, params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const quickCommands = [
    { name: 'List Directory', command: 'list_directory', params: '{"path": "/home/user/documents"}' },
    { name: 'Read File', command: 'read_file', params: '{"path": "/home/user/documents/test.txt"}' },
    { name: 'Write File', command: 'write_file', params: '{"path": "/home/user/documents/output.txt", "content": "Hello from secure agent!"}' }
  ];

  return (
    <Grid container spacing={3}>
      {/* Agent Status */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Security color="primary" />
              <Typography variant="h6">Agent Status</Typography>
              <Chip label="Active" color="success" size="small" />
            </Box>
            {capabilities && (
              <Box mt={2}>
                <Typography variant="body2" color="textSecondary">
                  Agent ID: {capabilities.agent_id}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Session: {capabilities.session_id}
                </Typography>
                <Box mt={1}>
                  {capabilities.security_features?.map((feature) => (
                    <Chip key={feature} label={feature} size="small" sx={{ mr: 1, mb: 1 }} />
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Command Interface */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <Build sx={{ mr: 1, verticalAlign: 'middle' }} />
            Execute Agent Command
          </Typography>
          
          <TextField
            fullWidth
            label="Command"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            margin="normal"
            placeholder="e.g., read_file, list_directory"
          />
          
          <TextField
            fullWidth
            label="Parameters (JSON)"
            value={parameters}
            onChange={(e) => setParameters(e.target.value)}
            margin="normal"
            multiline
            rows={3}
          />
          
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={executeCommand}
            disabled={loading || !command}
            sx={{ mt: 2 }}
          >
            {loading ? 'Executing...' : 'Execute Command'}
          </Button>

          {/* Quick Commands */}
          <Box mt={3}>
            <Typography variant="subtitle2" gutterBottom>
              Quick Commands:
            </Typography>
            {quickCommands.map((cmd) => (
              <Button
                key={cmd.name}
                variant="outlined"
                size="small"
                onClick={() => {
                  setCommand(cmd.command);
                  setParameters(cmd.params);
                }}
                sx={{ mr: 1, mb: 1 }}
              >
                {cmd.name}
              </Button>
            ))}
          </Box>
        </Paper>
      </Grid>

      {/* Results */}
      <Grid item xs={12} md={6}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Execution Result
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {result && (
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              <JSONPretty
                data={result}
                theme="monikai"
              />
            </Box>
          )}
        </Paper>
      </Grid>

      {/* Available Tools */}
      {capabilities && (
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Available Tools
            </Typography>
            <Grid container spacing={2}>
              {capabilities.available_tools?.map((tool) => (
                <Grid item key={tool}>
                  <Chip label={tool} variant="outlined" />
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      )}
    </Grid>
  );
}

export default AgentDashboard;
