import React from 'react';
import { 
  Paper, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Chip,
  Link
} from '@mui/material';

function MonitoringPanel({ data }) {
  const formatPrice = (price) => {
    return price ? `$${price.toFixed(2)}` : 'N/A';
  };

  const formatUrl = (url) => {
    try {
      const domain = new URL(url).hostname;
      return domain.replace('www.', '');
    } catch {
      return url;
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Monitoring Results
      </Typography>
      
      {data.length === 0 ? (
        <Typography color="textSecondary">
          No monitoring data available. Add some URLs to start monitoring!
        </Typography>
      ) : (
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Product</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Price</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Circuit Breaker</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((result, index) => (
                <TableRow key={index}>
                  <TableCell>
                    {result.success && result.data ? 
                      (result.data.title || 'Unknown Product') : 
                      'Failed to fetch'
                    }
                  </TableCell>
                  <TableCell>
                    {result.success && result.data ? 
                      formatUrl(result.data.url) : 
                      'N/A'
                    }
                  </TableCell>
                  <TableCell>
                    {result.success && result.data ? 
                      formatPrice(result.data.price) : 
                      'N/A'
                    }
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={result.success ? 'Success' : 'Failed'} 
                      color={result.success ? 'success' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {result.circuit_breaker_stats && (
                      <Chip 
                        label={result.circuit_breaker_stats.state}
                        size="small"
                        color={result.circuit_breaker_stats.state === 'CLOSED' ? 'success' : 'warning'}
                      />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
}

export default MonitoringPanel;
