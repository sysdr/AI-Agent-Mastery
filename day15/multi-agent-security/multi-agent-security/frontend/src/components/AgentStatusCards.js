import React from 'react';
import { Grid, Card, CardContent, Typography, Box, Chip, LinearProgress } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';
import EditIcon from '@mui/icons-material/Edit';
import RateReviewIcon from '@mui/icons-material/RateReview';
import ManageAccountsIcon from '@mui/icons-material/ManageAccounts';

const AgentStatusCards = ({ agents = [] }) => {
  const getAgentIcon = (type) => {
    const icons = {
      writer: <PersonIcon />,
      editor: <EditIcon />,
      reviewer: <RateReviewIcon />,
      coordinator: <ManageAccountsIcon />
    };
    return icons[type] || <PersonIcon />;
  };

  const getStatusColor = (status) => {
    return status === 'active' ? 'success' : 'error';
  };

  return (
    <Grid container spacing={2}>
      {agents.map((agent) => (
        <Grid item xs={12} sm={6} md={4} key={agent.id}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                {getAgentIcon(agent.type)}
                <Box ml={1}>
                  <Typography variant="h6">{agent.name}</Typography>
                  <Chip
                    label={agent.status}
                    color={getStatusColor(agent.status)}
                    size="small"
                  />
                </Box>
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Type: {agent.type}
              </Typography>

              {/* Usage Stats */}
              {agent.usage_stats && (
                <Box mt={2}>
                  <Typography variant="body2" gutterBottom>
                    Resource Usage
                  </Typography>
                  {Object.entries(agent.usage_stats).map(([resource, stats]) => (
                    <Box key={resource} mb={1}>
                      <Box display="flex" justifyContent="space-between">
                        <Typography variant="caption">
                          {resource.replace('_', ' ')}
                        </Typography>
                        <Typography variant="caption">
                          {stats.used.toFixed(1)}/{stats.limit}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(stats.percentage, 100)}
                        color={stats.percentage > 80 ? 'error' : 'primary'}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default AgentStatusCards;
