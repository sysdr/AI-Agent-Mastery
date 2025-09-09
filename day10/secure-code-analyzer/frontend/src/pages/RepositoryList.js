import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
} from '@mui/material';
import { Refresh as RefreshIcon, Add as AddIcon } from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE = 'http://localhost:8000/api';

const RepositoryList = () => {
  const [open, setOpen] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const queryClient = useQueryClient();

  const { data: repositories, isLoading } = useQuery(
    'repositories',
    () => axios.get(`${API_BASE}/git/repositories`).then(res => res.data.repositories)
  );

  const analyzeRepoMutation = useMutation(
    (data) => axios.post(`${API_BASE}/git/analyze-repository`, data),
    {
      onSuccess: () => {
        toast.success('Repository analysis started');
        queryClient.invalidateQueries('repositories');
        setOpen(false);
        setRepoUrl('');
        setBranch('main');
      },
      onError: () => toast.error('Failed to start analysis'),
    }
  );

  const handleAnalyze = () => {
    if (!repoUrl) {
      toast.error('Repository URL is required');
      return;
    }
    analyzeRepoMutation.mutate({ repo_url: repoUrl, branch });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'clean': return 'success';
      case 'needs_attention': return 'warning';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Repository Security Status
        </Typography>
        <Box>
          <IconButton onClick={() => queryClient.invalidateQueries('repositories')}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpen(true)}
            sx={{ ml: 1 }}
          >
            Analyze Repository
          </Button>
        </Box>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Repository</TableCell>
                <TableCell>Last Scan</TableCell>
                <TableCell>Findings</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {repositories?.map((repo) => (
                <TableRow key={repo.id}>
                  <TableCell>
                    <Typography variant="body1" fontWeight="bold">
                      {repo.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {repo.url}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {new Date(repo.last_scan).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={repo.findings}
                      color={repo.findings > 10 ? 'error' : repo.findings > 5 ? 'warning' : 'success'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={repo.status.replace('_', ' ')}
                      color={getStatusColor(repo.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      size="small"
                      onClick={() => {
                        setRepoUrl(repo.url);
                        setOpen(true);
                      }}
                    >
                      Re-scan
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {!repositories?.length && !isLoading && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography color="textSecondary">
                      No repositories found. Add one to get started.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Add Repository Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Analyze Repository</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Repository URL"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/user/repo.git"
            sx={{ mb: 2, mt: 1 }}
          />
          <TextField
            fullWidth
            label="Branch"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleAnalyze}
            disabled={analyzeRepoMutation.isLoading}
          >
            {analyzeRepoMutation.isLoading ? 'Analyzing...' : 'Start Analysis'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RepositoryList;
