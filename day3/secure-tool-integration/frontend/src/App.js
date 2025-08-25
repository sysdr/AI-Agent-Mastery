import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Tab,
  Tabs
} from '@mui/material';
import AgentDashboard from './components/AgentDashboard';
import SecurityPanel from './components/SecurityPanel';
import ToolRegistry from './components/ToolRegistry';
import AuditLogs from './components/AuditLogs';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <div>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🛡️ Secure Tool Integration Dashboard
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        <Paper sx={{ width: '100%' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label="Agent Dashboard" />
            <Tab label="Security Panel" />
            <Tab label="Tool Registry" />
            <Tab label="Audit Logs" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <AgentDashboard />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <SecurityPanel />
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            <ToolRegistry />
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            <AuditLogs />
          </TabPanel>
        </Paper>
      </Container>
    </div>
  );
}

export default App;
