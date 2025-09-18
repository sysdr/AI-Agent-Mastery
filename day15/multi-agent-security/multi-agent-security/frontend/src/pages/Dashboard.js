import React from 'react';
import { Container, Grid, Paper, Typography, Box } from '@mui/material';
import { useQuery } from 'react-query';
import axios from 'axios';
import AgentStatusCards from '../components/AgentStatusCards';
import SystemMetrics from '../components/SystemMetrics';
import RecentActivity from '../components/RecentActivity';

const Dashboard = () => {
  const { data: systemStatus } = useQuery('systemStatus', () =>
    axios.get('/system/status').then(res => res.data)
  );

  const { data: agents } = useQuery('agents', () =>
    axios.get('/agents').then(res => res.data)
  );

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Security Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* System Status */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Box display="flex" gap={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Security
                </Typography>
                <Typography variant="h6" color="success.main">
                  {systemStatus?.security || 'Loading...'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Encryption
                </Typography>
                <Typography variant="h6" color="success.main">
                  {systemStatus?.encryption || 'Loading...'}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Quota Management
                </Typography>
                <Typography variant="h6" color="success.main">
                  {systemStatus?.quota_management || 'Loading...'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Agent Status Cards */}
        <Grid item xs={12} md={8}>
          <AgentStatusCards agents={agents} />
        </Grid>

        {/* System Metrics */}
        <Grid item xs={12} md={4}>
          <SystemMetrics />
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <RecentActivity />
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
