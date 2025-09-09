import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
} from '@mui/material';
import toast from 'react-hot-toast';

const Settings = () => {
  const [settings, setSettings] = useState({
    geminiApiKey: '',
    webhookSecret: '',
    autoScan: true,
    emailNotifications: false,
    slackWebhook: '',
    maxFileSize: 1,
  });

  const handleSave = () => {
    // In a real app, this would save to backend
    toast.success('Settings saved successfully');
  };

  const handleChange = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Grid container spacing={3}>
        {/* API Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Configuration
              </Typography>
              <TextField
                fullWidth
                label="Gemini API Key"
                type="password"
                value={settings.geminiApiKey}
                onChange={(e) => handleChange('geminiApiKey', e.target.value)}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Webhook Secret"
                type="password"
                value={settings.webhookSecret}
                onChange={(e) => handleChange('webhookSecret', e.target.value)}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Scan Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Scan Settings
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoScan}
                    onChange={(e) => handleChange('autoScan', e.target.checked)}
                  />
                }
                label="Auto-scan on push"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Max File Size (MB)"
                type="number"
                value={settings.maxFileSize}
                onChange={(e) => handleChange('maxFileSize', parseInt(e.target.value))}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Notifications */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notifications
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.emailNotifications}
                    onChange={(e) => handleChange('emailNotifications', e.target.checked)}
                  />
                }
                label="Email notifications"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="Slack Webhook URL"
                value={settings.slackWebhook}
                onChange={(e) => handleChange('slackWebhook', e.target.value)}
                placeholder="https://hooks.slack.com/services/..."
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Save Button */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Button variant="contained" onClick={handleSave}>
              Save Settings
            </Button>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Settings;
