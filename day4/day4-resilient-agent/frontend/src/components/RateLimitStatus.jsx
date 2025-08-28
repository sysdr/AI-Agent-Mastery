import React, { useState, useEffect } from 'react';
import { Paper, Typography, LinearProgress, Box, Grid } from '@mui/material';

function RateLimitStatus() {
  const [rateLimits, setRateLimits] = useState({});

  useEffect(() => {
    // Simulate rate limit data - in real app, fetch from API
    const mockData = {
      'amazon.com': { current: 7, limit: 10, reset_time: Date.now() + 300000 },
      'ebay.com': { current: 3, limit: 10, reset_time: Date.now() + 300000 },
      'walmart.com': { current: 1, limit: 10, reset_time: Date.now() + 300000 }
    };
    setRateLimits(mockData);
  }, []);

  const getUsagePercentage = (current, limit) => {
    return (current / limit) * 100;
  };

  const getProgressColor = (percentage) => {
    if (percentage < 50) return 'success';
    if (percentage < 80) return 'warning';
    return 'error';
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Rate Limit Status
      </Typography>
      
      <Grid container spacing={2}>
        {Object.entries(rateLimits).map(([domain, data]) => {
          const percentage = getUsagePercentage(data.current, data.limit);
          
          return (
            <Grid item xs={12} sm={6} md={4} key={domain}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  {domain}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" color="textSecondary" sx={{ minWidth: 80 }}>
                    {data.current} / {data.limit}
                  </Typography>
                  <Box sx={{ flexGrow: 1, ml: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={percentage} 
                      color={getProgressColor(percentage)}
                    />
                  </Box>
                </Box>
                <Typography variant="caption" color="textSecondary">
                  Resets in {Math.round((data.reset_time - Date.now()) / 60000)}m
                </Typography>
              </Box>
            </Grid>
          );
        })}
      </Grid>
    </Paper>
  );
}

export default RateLimitStatus;
