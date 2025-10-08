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
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  Tab,
  Tabs,
} from '@mui/material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useMutation } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE = 'http://localhost:8000/api';

const CodeAnalysis = () => {
  const [code, setCode] = useState(`# Example vulnerable Python code
import sqlite3
import sys

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return result

# Hardcoded secret vulnerability  
API_SECRET = "sk-1234567890abcdef"
DATABASE_PASSWORD = "supersecretpassword123"

def unsafe_eval_example(user_input):
    # Code injection vulnerability
    result = eval(user_input)
    return result
`);
  const [fileName, setFileName] = useState('example.py');
  const [tabValue, setTabValue] = useState(0);

  const analyzeCodeMutation = useMutation(
    (data) => axios.post(`${API_BASE}/security/analyze-code`, data),
    {
      onSuccess: () => toast.success('Code analysis completed'),
      onError: () => toast.error('Analysis failed'),
    }
  );

  const explainFindingMutation = useMutation(
    (data) => axios.post(`${API_BASE}/security/explain-finding`, data),
    {
      onSuccess: () => toast.success('Explanation generated'),
      onError: () => toast.error('Failed to generate explanation'),
    }
  );

  const handleAnalyze = () => {
    analyzeCodeMutation.mutate({
      code,
      file_path: fileName,
    });
  };

  const handleExplainFinding = (finding) => {
    explainFindingMutation.mutate(finding);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const results = analyzeCodeMutation.data?.data;
  const explanation = explainFindingMutation.data?.data?.explanation;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Code Security Analysis
      </Typography>

      <Grid container spacing={3}>
        {/* Code Input */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Code Input
            </Typography>
            <TextField
              fullWidth
              label="File Name"
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              multiline
              rows={20}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste your code here..."
              sx={{ mb: 2, fontFamily: 'monospace' }}
            />
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={analyzeCodeMutation.isLoading}
            >
              {analyzeCodeMutation.isLoading ? 'Analyzing...' : 'Analyze Code'}
            </Button>
          </Paper>
        </Grid>

        {/* Results */}
        <Grid item xs={12} lg={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Analysis Results
            </Typography>

            {results && (
              <>
                {/* Summary */}
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6">Summary</Typography>
                    <Box display="flex" gap={1} mt={1}>
                      <Chip label={`Critical: ${results.summary.critical}`} color="error" size="small" />
                      <Chip label={`High: ${results.summary.high}`} color="warning" size="small" />
                      <Chip label={`Medium: ${results.summary.medium}`} color="info" size="small" />
                      <Chip label={`Low: ${results.summary.low}`} color="success" size="small" />
                    </Box>
                  </CardContent>
                </Card>

                {/* Findings */}
                {results.findings.length > 0 ? (
                  <List>
                    {results.findings.map((finding, index) => (
                      <React.Fragment key={index}>
                        <ListItem sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <Chip
                              label={finding.severity}
                              color={getSeverityColor(finding.severity)}
                              size="small"
                            />
                            <Typography variant="body2" color="textSecondary">
                              Line {finding.line_number}
                            </Typography>
                          </Box>
                          <Typography variant="body1" fontWeight="bold">
                            {finding.message}
                          </Typography>
                          <SyntaxHighlighter
                            language="python"
                            style={tomorrow}
                            customStyle={{ fontSize: '12px', margin: '8px 0' }}
                          >
                            {finding.code_snippet}
                          </SyntaxHighlighter>
                          <Typography variant="body2" color="textSecondary">
                            {finding.recommendation}
                          </Typography>
                          <Button
                            size="small"
                            onClick={() => handleExplainFinding(finding)}
                            sx={{ mt: 1 }}
                          >
                            Explain Finding
                          </Button>
                        </ListItem>
                        {index < results.findings.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Alert severity="success">No security issues found!</Alert>
                )}
              </>
            )}

            {/* AI Explanation */}
            {explanation && (
              <Paper sx={{ p: 2, mt: 2, bgcolor: 'background.default' }}>
                <Typography variant="h6" gutterBottom>
                  AI Explanation
                </Typography>
                <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                  {explanation}
                </Typography>
              </Paper>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CodeAnalysis;
