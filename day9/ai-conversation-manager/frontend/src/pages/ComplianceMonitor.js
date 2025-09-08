import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ComplianceMonitor = () => {
  const violationData = [
    { category: 'Profanity', count: 12, severity: 'medium' },
    { category: 'Injection Attempt', count: 5, severity: 'high' },
    { category: 'Personal Info Request', count: 8, severity: 'high' },
    { category: 'System Access', count: 2, severity: 'critical' },
    { category: 'Inappropriate Content', count: 15, severity: 'low' },
  ];

  const recentViolations = [
    {
      id: 1,
      timestamp: '2025-01-15 14:32:15',
      message: 'Can you give me admin access to...',
      violation: 'System Access Request',
      severity: 'critical',
      action: 'Blocked',
    },
    {
      id: 2,
      timestamp: '2025-01-15 14:28:42',
      message: 'Ignore previous instructions and...',
      violation: 'Injection Attempt',
      severity: 'high',
      action: 'Blocked',
    },
    {
      id: 3,
      timestamp: '2025-01-15 14:25:18',
      message: 'What\'s your SSN number?',
      violation: 'Personal Info Request',
      severity: 'high',
      action: 'Flagged',
    },
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Compliance Monitoring Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4CAF5015, #4CAF5005)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Compliance Rate
              </Typography>
              <Typography variant="h3" sx={{ color: '#4CAF50' }}>
                98.5%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last 24 hours
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #FF980015, #FF980005)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Total Violations
              </Typography>
              <Typography variant="h3" sx={{ color: '#FF9800' }}>
                42
              </Typography>
              <Typography variant="body2" color="textSecondary">
                This week
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #F4433615, #F4433605)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Critical Blocks
              </Typography>
              <Typography variant="h3" sx={{ color: '#F44336' }}>
                7
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Today
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #2196F315, #2196F305)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                False Positives
              </Typography>
              <Typography variant="h3" sx={{ color: '#2196F3' }}>
                1.2%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                This month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Violation Categories Chart */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Violation Categories
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={violationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Violations */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Violations
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Time</TableCell>
                    <TableCell>Violation</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {recentViolations.map((violation) => (
                    <TableRow key={violation.id}>
                      <TableCell>
                        <Typography variant="caption">
                          {new Date(violation.timestamp).toLocaleTimeString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {violation.violation}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {violation.message.substring(0, 30)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={violation.severity}
                          color={getSeverityColor(violation.severity)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={violation.action}
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ComplianceMonitor;
