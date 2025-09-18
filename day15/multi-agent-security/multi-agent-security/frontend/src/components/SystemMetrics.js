import React from 'react';
import { Paper, Typography, Box } from '@mui/material';

const SystemMetrics = () => (
  <Paper sx={{ p: 3 }}>
    <Typography variant="h6" gutterBottom>System Metrics</Typography>
    <Box>
      <Typography variant="body2">Encryption: Active</Typography>
      <Typography variant="body2">Agents: Online</Typography>
      <Typography variant="body2">Security: Enabled</Typography>
    </Box>
  </Paper>
);

export default SystemMetrics;
