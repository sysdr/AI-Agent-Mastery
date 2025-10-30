import React from 'react';
import { Typography, Box, LinearProgress, Stack } from '@mui/material';
import { useQuery } from 'react-query';
import axios from 'axios';

const ComplianceOverview: React.FC = () => {
  const { data: complianceData } = useQuery(
    'compliance-report',
    () => axios.get('http://localhost:8000/compliance/report').then(res => res.data)
  );

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Compliance Score
      </Typography>
      <Stack spacing={2}>
        <Box>
          <Typography variant="body2">Overall Score</Typography>
          <LinearProgress 
            variant="determinate" 
            value={complianceData?.compliance_score || 0}
            sx={{ height: 10, borderRadius: 1 }}
          />
          <Typography variant="body2" sx={{ mt: 1 }}>
            {complianceData?.compliance_score?.toFixed(1) || 0}%
          </Typography>
        </Box>
        
        <Box>
          <Typography variant="body2">Violations: {complianceData?.violation_count || 0}</Typography>
          <Typography variant="body2">Total Events: {complianceData?.total_events || 0}</Typography>
        </Box>
      </Stack>
    </Box>
  );
};

export default ComplianceOverview;
