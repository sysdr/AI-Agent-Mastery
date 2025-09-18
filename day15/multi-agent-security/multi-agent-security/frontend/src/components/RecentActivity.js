import React from 'react';
import { Paper, Typography, List, ListItem, ListItemText } from '@mui/material';

const RecentActivity = () => (
  <Paper sx={{ p: 3 }}>
    <Typography variant="h6" gutterBottom>Recent Activity</Typography>
    <List>
      <ListItem><ListItemText primary="Agent communication encrypted" /></ListItem>
      <ListItem><ListItemText primary="Content workflow initiated" /></ListItem>
      <ListItem><ListItemText primary="Security audit completed" /></ListItem>
    </List>
  </Paper>
);

export default RecentActivity;
