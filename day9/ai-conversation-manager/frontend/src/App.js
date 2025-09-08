import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import Dashboard from './pages/Dashboard';
import ConversationChat from './pages/ConversationChat';
import ComplianceMonitor from './pages/ComplianceMonitor';
import PersonalityAnalysis from './pages/PersonalityAnalysis';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" sx={{ background: 'linear-gradient(45deg, #667eea, #764ba2)' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🤖 AI Conversation Manager - Advanced Production System
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Paper elevation={3} sx={{ borderRadius: 2 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="📊 Dashboard" />
            <Tab label="💬 Conversation" />
            <Tab label="🛡️ Compliance" />
            <Tab label="🧠 Personality" />
          </Tabs>

          <TabPanel value={activeTab} index={0}>
            <Dashboard />
          </TabPanel>
          <TabPanel value={activeTab} index={1}>
            <ConversationChat />
          </TabPanel>
          <TabPanel value={activeTab} index={2}>
            <ComplianceMonitor />
          </TabPanel>
          <TabPanel value={activeTab} index={3}>
            <PersonalityAnalysis />
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
}

export default App;
