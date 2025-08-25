import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Box,
  Button
} from '@mui/material';
import { Refresh, Security } from '@mui/icons-material';
import ApiService from '../services/ApiService';

function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const response = await ApiService.getAuditLogs();
      setLogs(response.logs);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSecurityLevelColor = (level) => {
    switch (level) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Grid container spacing={3}>
      {/* Audit Overview */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={2}>
              <Security color="primary" />
              <Typography variant="h6">Security Audit Logs</Typography>
              <Chip label={`${logs.length} Events`} color="primary" size="small" />
            </Box>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadLogs}
              disabled={loading}
            >
              Refresh
            </Button>
          </Box>
        </Paper>
      </Grid>

      {/* Audit Log Table */}
      <Grid item xs={12}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Agent ID</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Result</TableCell>
                <TableCell>Security Level</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>
                    <Typography variant="body2">
                      {formatTimestamp(log.timestamp)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={log.agent_id} size="small" />
                  </TableCell>
                  <TableCell>{log.action}</TableCell>
                  <TableCell>{log.resource}</TableCell>
                  <TableCell>
                    <Chip
                      label={log.result}
                      color={log.result === 'success' ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={log.security_level}
                      color={getSecurityLevelColor(log.security_level)}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Grid>
    </Grid>
  );
}

export default AuditLogs;
