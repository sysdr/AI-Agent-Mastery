import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Chip,
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

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalConversations: 1247,
    complianceRate: 98.5,
    personalityConsistency: 96.2,
    averageResponseTime: 245,
    escalationRate: 2.3,
  });

  const conversationData = [
    { time: '09:00', conversations: 45, compliance: 98 },
    { time: '10:00', conversations: 52, compliance: 97 },
    { time: '11:00', conversations: 48, compliance: 99 },
    { time: '12:00', conversations: 41, compliance: 98 },
    { time: '13:00', conversations: 55, compliance: 96 },
    { time: '14:00', conversations: 62, compliance: 99 },
    { time: '15:00', conversations: 58, compliance: 97 },
  ];

  const complianceBreakdown = [
    { name: 'Valid', value: 95.2, color: '#4CAF50' },
    { name: 'Flagged', value: 3.1, color: '#FF9800' },
    { name: 'Blocked', value: 1.7, color: '#F44336' },
  ];

  const MetricCard = ({ title, value, unit, color, trend }) => (
    <Card sx={{ height: '100%', background: `linear-gradient(135deg, ${color}15, ${color}05)` }}>
      <CardContent>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h3" component="div" sx={{ color: color }}>
          {value}
          <Typography variant="h6" component="span" sx={{ ml: 1 }}>
            {unit}
          </Typography>
        </Typography>
        {trend && (
          <Chip
            label={trend}
            size="small"
            color={trend.includes('+') ? 'success' : 'error'}
            sx={{ mt: 1 }}
          />
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        System Overview Dashboard
      </Typography>

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Total Conversations"
            value={metrics.totalConversations}
            unit=""
            color="#667eea"
            trend="+12% today"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Compliance Rate"
            value={metrics.complianceRate}
            unit="%"
            color="#4CAF50"
            trend="+0.5%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Personality Consistency"
            value={metrics.personalityConsistency}
            unit="%"
            color="#2196F3"
            trend="+1.2%"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Avg Response Time"
            value={metrics.averageResponseTime}
            unit="ms"
            color="#FF9800"
            trend="-15ms"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <MetricCard
            title="Escalation Rate"
            value={metrics.escalationRate}
            unit="%"
            color="#9C27B0"
            trend="-0.3%"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              Real-time Conversation Activity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={conversationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="conversations"
                  stroke="#667eea"
                  strokeWidth={3}
                  name="Conversations"
                />
                <Line
                  type="monotone"
                  dataKey="compliance"
                  stroke="#4CAF50"
                  strokeWidth={2}
                  name="Compliance %"
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Compliance Breakdown
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={complianceBreakdown}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {complianceBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Health Status
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="textSecondary">
                    API Response Time
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={85}
                    sx={{ height: 8, borderRadius: 4, bgcolor: '#e0e0e0' }}
                  />
                  <Typography variant="caption">Excellent (85/100)</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="textSecondary">
                    Memory Usage
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={62}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="caption">Normal (62%)</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="textSecondary">
                    CPU Usage
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={45}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="caption">Low (45%)</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="textSecondary">
                    Error Rate
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={5}
                    color="success"
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="caption">Low (0.01%)</Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
