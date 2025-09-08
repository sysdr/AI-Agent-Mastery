import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

const PersonalityAnalysis = () => {
  const consistencyData = [
    { time: '09:00', consistency: 96, technical: 85, politeness: 92 },
    { time: '10:00', consistency: 94, technical: 88, politeness: 89 },
    { time: '11:00', consistency: 97, technical: 92, politeness: 95 },
    { time: '12:00', consistency: 95, technical: 87, politeness: 93 },
    { time: '13:00', consistency: 92, technical: 84, politeness: 88 },
    { time: '14:00', consistency: 98, technical: 94, politeness: 97 },
  ];

  const personalityProfile = [
    { trait: 'Technical Expertise', value: 92, max: 100 },
    { trait: 'Helpfulness', value: 96, max: 100 },
    { trait: 'Professionalism', value: 94, max: 100 },
    { trait: 'Consistency', value: 89, max: 100 },
    { trait: 'Clarity', value: 91, max: 100 },
    { trait: 'Engagement', value: 87, max: 100 },
  ];

  const anomalies = [
    {
      id: 1,
      timestamp: '2025-01-15 14:15:22',
      session: 'session_12345',
      type: 'tone_shift',
      description: 'Sudden increase in technical terminology usage',
      severity: 'low',
      resolved: true,
    },
    {
      id: 2,
      timestamp: '2025-01-15 13:42:18',
      session: 'session_12340',
      type: 'length_anomaly',
      description: 'Response length 300% above baseline',
      severity: 'medium',
      resolved: false,
    },
    {
      id: 3,
      timestamp: '2025-01-15 13:28:45',
      session: 'session_12338',
      type: 'politeness_shift',
      description: 'Decrease in politeness markers detected',
      severity: 'low',
      resolved: true,
    },
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        AI Personality Analysis Dashboard
      </Typography>

      {/* Summary Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea15, #667eea05)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Overall Consistency
              </Typography>
              <Typography variant="h3" sx={{ color: '#667eea' }}>
                96.2%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={96.2}
                sx={{ mt: 1, borderRadius: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4CAF5015, #4CAF5005)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Anomalies Detected
              </Typography>
              <Typography variant="h3" sx={{ color: '#4CAF50' }}>
                3
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Today (2 resolved)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #FF980015, #FF980005)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Personality Drift
              </Typography>
              <Typography variant="h3" sx={{ color: '#FF9800' }}>
                0.8%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                This week
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #9C27B015, #9C27B005)' }}>
            <CardContent>
              <Typography variant="h6" color="textSecondary">
                Recalibrations
              </Typography>
              <Typography variant="h3" sx={{ color: '#9C27B0' }}>
                2
              </Typography>
              <Typography variant="body2" color="textSecondary">
                This month
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Consistency Trend */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Personality Consistency Trends
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={consistencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[80, 100]} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="consistency"
                  stroke="#667eea"
                  strokeWidth={3}
                  name="Overall Consistency"
                />
                <Line
                  type="monotone"
                  dataKey="technical"
                  stroke="#4CAF50"
                  strokeWidth={2}
                  name="Technical Tone"
                />
                <Line
                  type="monotone"
                  dataKey="politeness"
                  stroke="#FF9800"
                  strokeWidth={2}
                  name="Politeness"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Personality Profile Radar */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Personality Profile
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={personalityProfile}>
                <PolarGrid />
                <PolarAngleAxis dataKey="trait" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis domain={[60, 100]} tick={false} />
                <Radar
                  name="Current"
                  dataKey="value"
                  stroke="#667eea"
                  fill="#667eea"
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Behavioral Anomalies */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Behavioral Anomalies
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Session ID</TableCell>
                    <TableCell>Anomaly Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {anomalies.map((anomaly) => (
                    <TableRow key={anomaly.id}>
                      <TableCell>
                        <Typography variant="body2">
                          {new Date(anomaly.timestamp).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {anomaly.session}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={anomaly.type.replace('_', ' ')}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {anomaly.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={anomaly.severity}
                          color={getSeverityColor(anomaly.severity)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={anomaly.resolved ? 'Resolved' : 'Active'}
                          color={anomaly.resolved ? 'success' : 'warning'}
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

export default PersonalityAnalysis;
