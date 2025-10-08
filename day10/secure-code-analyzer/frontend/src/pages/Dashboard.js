import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
} from 'recharts';
import { useQuery } from 'react-query';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const Dashboard = () => {
  const { data: dashboardData, isLoading } = useQuery(
    'dashboard-data',
    () => axios.get(`${API_BASE}/analysis/dashboard-data`).then(res => res.data),
    { refetchInterval: 30000 }
  );

  const { data: securityStats } = useQuery(
    'security-stats',
    () => axios.get(`${API_BASE}/security/stats`).then(res => res.data)
  );

  const vulnerabilityColors = {
    critical: '#ff1744',
    high: '#ff9100',
    medium: '#ffc107',
    low: '#4caf50',
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  const trendData = dashboardData?.vulnerability_trends ? 
    dashboardData.vulnerability_trends.labels.map((label, index) => ({
      name: label,
      Critical: dashboardData.vulnerability_trends.critical[index],
      High: dashboardData.vulnerability_trends.high[index],
      Medium: dashboardData.vulnerability_trends.medium[index],
      Low: dashboardData.vulnerability_trends.low[index],
    })) : [];

  const severityData = securityStats ? [
    { name: 'Critical', value: 3, color: '#ff1744' },
    { name: 'High', value: 8, color: '#ff9100' },
    { name: 'Medium', value: 15, color: '#ffc107' },
    { name: 'Low', value: 22, color: '#4caf50' },
  ] : [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Security Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Scans
              </Typography>
              <Typography variant="h4">
                {securityStats?.total_scans || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Vulnerabilities
              </Typography>
              <Typography variant="h4" color="error">
                {securityStats?.vulnerabilities_found || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Files Analyzed
              </Typography>
              <Typography variant="h4">
                {securityStats?.files_analyzed || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Repositories
              </Typography>
              <Typography variant="h4">
                {securityStats?.repositories_scanned || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Vulnerability Trends */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Vulnerability Trends (Last 5 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Critical" fill="#ff1744" />
                <Bar dataKey="High" fill="#ff9100" />
                <Bar dataKey="Medium" fill="#ffc107" />
                <Bar dataKey="Low" fill="#4caf50" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Severity Distribution */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Severity Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  label
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Scans */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Scans
            </Typography>
            <List>
              {dashboardData?.recent_scans?.map((scan) => (
                <ListItem key={scan.id}>
                  <ListItemText
                    primary={scan.repository}
                    secondary={`${scan.findings} findings - ${new Date(scan.timestamp).toLocaleString()}`}
                  />
                  <Chip
                    label={scan.status}
                    color={scan.status === 'completed' ? 'success' : 'warning'}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Top Vulnerabilities */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Vulnerabilities
            </Typography>
            <List>
              {dashboardData?.top_vulnerabilities?.map((vuln, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={vuln.type}
                    secondary={`${vuln.count} occurrences`}
                  />
                  <Chip
                    label={vuln.severity}
                    color={vuln.severity === 'critical' ? 'error' : vuln.severity === 'high' ? 'warning' : 'info'}
                    size="small"
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
