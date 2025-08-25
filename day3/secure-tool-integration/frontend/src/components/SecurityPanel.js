import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { Shield, Policy, Lock } from '@mui/icons-material';
import ApiService from '../services/ApiService';

function SecurityPanel() {
  const [permissions, setPermissions] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPermissions();
  }, []);

  const loadPermissions = async () => {
    try {
      const response = await ApiService.getPermissions();
      setPermissions(response.permissions);
    } catch (err) {
      console.error('Failed to load permissions:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>Loading security information...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      {/* Security Overview */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Shield color="primary" />
              <Typography variant="h6">Security Status</Typography>
              <Chip label="Secure" color="success" size="small" />
            </Box>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              All security policies active. Permission boundaries enforced.
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Permission Policies */}
      {permissions && Object.entries(permissions).map(([agentId, policy]) => (
        <Grid item xs={12} md={6} key={agentId}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Policy sx={{ mr: 1, verticalAlign: 'middle' }} />
              {agentId} Policy
            </Typography>
            
            <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
              Permissions:
            </Typography>
            <List dense>
              {policy.permissions?.map((perm, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={`${perm.resource}.${perm.action}`}
                    secondary={JSON.stringify(perm.constraints)}
                  />
                </ListItem>
              ))}
            </List>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="subtitle2" gutterBottom>
              Resource Limits:
            </Typography>
            <Box>
              {Object.entries(policy.resource_limits || {}).map(([key, value]) => (
                <Chip
                  key={key}
                  label={`${key}: ${value}`}
                  variant="outlined"
                  size="small"
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Paper>
        </Grid>
      ))}

      {/* Security Features */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            <Lock sx={{ mr: 1, verticalAlign: 'middle' }} />
            Active Security Features
          </Typography>
          
          <Grid container spacing={2}>
            {[
              'Permission Boundaries',
              'Audit Logging',
              'Tool Sandboxing',
              'Input Validation',
              'Resource Monitoring',
              'Error Containment'
            ].map((feature) => (
              <Grid item key={feature}>
                <Chip
                  label={feature}
                  color="primary"
                  variant="outlined"
                />
              </Grid>
            ))}
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default SecurityPanel;
