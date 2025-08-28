import React from 'react';
import { Paper, Typography, Grid, Chip, Box } from '@mui/material';

function CircuitBreakerStatus({ data }) {
  const getStateColor = (state) => {
    switch (state) {
      case 'CLOSED': return 'success';
      case 'OPEN': return 'error';
      case 'HALF_OPEN': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Circuit Breaker Status
      </Typography>
      
      {Object.keys(data).length === 0 ? (
        <Typography color="textSecondary">
          No circuit breakers active
        </Typography>
      ) : (
        <Grid container spacing={2}>
          {Object.entries(data).map(([domain, stats]) => (
            <Grid item xs={12} sm={6} md={4} key={domain}>
              <Box sx={{ border: 1, borderColor: 'divider', borderRadius: 1, p: 1 }}>
                <Typography variant="subtitle1" gutterBottom>
                  {domain}
                </Typography>
                <Box sx={{ mb: 1 }}>
                  <Chip 
                    label={stats.state} 
                    size="small"
                    color={getStateColor(stats.state)}
                  />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  Failures: {stats.failure_count}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Successes: {stats.success_count}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      )}
    </Paper>
  );
}

export default CircuitBreakerStatus;
