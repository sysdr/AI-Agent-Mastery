import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { Build, ExpandMore, CheckCircle, Warning } from '@mui/icons-material';
import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css';
import ApiService from '../services/ApiService';

function ToolRegistry() {
  const [tools, setTools] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const response = await ApiService.getToolRegistry();
      setTools(response.tools);
    } catch (err) {
      console.error('Failed to load tools:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Typography>Loading tool registry...</Typography>;
  }

  return (
    <Grid container spacing={3}>
      {/* Registry Overview */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Build color="primary" />
              <Typography variant="h6">Tool Registry</Typography>
              <Chip 
                label={`${Object.keys(tools || {}).length} Tools Registered`} 
                color="primary" 
                size="small" 
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Tool Details */}
      {tools && Object.entries(tools).map(([toolName, tool]) => (
        <Grid item xs={12} key={toolName}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" gap={2} width="100%">
                <Typography variant="h6">{tool.name}</Typography>
                <Chip
                  icon={tool.security_validated ? <CheckCircle /> : <Warning />}
                  label={tool.security_validated ? 'Validated' : 'Unvalidated'}
                  color={tool.security_validated ? 'success' : 'warning'}
                  size="small"
                />
                <Typography variant="body2" color="textSecondary" sx={{ ml: 'auto' }}>
                  {tool.description}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Required Permissions:
                    </Typography>
                    <Box>
                      {tool.required_permissions?.map((perm) => (
                        <Chip
                          key={perm}
                          label={perm}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Input Schema:
                    </Typography>
                    <JSONPretty
                      data={tool.input_schema}
                      theme="monikai"
                    />
                  </Paper>
                </Grid>
                
                <Grid item xs={12}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Output Schema:
                    </Typography>
                    <JSONPretty
                      data={tool.output_schema}
                      theme="monikai"
                    />
                  </Paper>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      ))}
    </Grid>
  );
}

export default ToolRegistry;
