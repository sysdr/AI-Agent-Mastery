import React from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  AppBar,
  Toolbar,
  Button
} from '@mui/material';
import { useAuth } from '../hooks/useAuth';
import { useQuery } from 'react-query';
import axios from 'axios';
import SecurityMetrics from '../components/SecurityMetrics';
import ComplianceOverview from '../components/ComplianceOverview';
import RecentIncidents from '../components/RecentIncidents';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();

  const { data: dashboardData, isLoading } = useQuery(
    'dashboard',
    () => axios.get('http://localhost:8000/security/dashboard').then(res => res.data),
    { refetchInterval: 30000 }
  );

  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Security Platform - Welcome {user?.username}
          </Typography>
          <Button color="inherit" onClick={logout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h4" gutterBottom>
              Security Dashboard
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="primary">
                  Incidents (24h)
                </Typography>
                <Typography variant="h3">
                  {dashboardData?.incidents_24h || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="success.main">
                  Auth Success Rate
                </Typography>
                <Typography variant="h3">
                  {dashboardData?.auth_success_rate?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="warning.main">
                  Active Threats
                </Typography>
                <Typography variant="h3">
                  {dashboardData?.active_threats || 0}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: 300 }}>
              <SecurityMetrics data={dashboardData} />
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, height: 300 }}>
              <ComplianceOverview />
            </Paper>
          </Grid>
          
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <RecentIncidents />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default DashboardPage;
