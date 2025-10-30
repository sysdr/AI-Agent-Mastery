import React from 'react';
import { Typography, Box } from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';

interface SecurityMetricsProps {
  data: any;
}

const SecurityMetrics: React.FC<SecurityMetricsProps> = ({ data }) => {
  const incidentData = data?.incident_counts ? [
    { name: 'Critical', value: data.incident_counts.critical, color: '#f44336' },
    { name: 'High', value: data.incident_counts.high, color: '#ff9800' },
    { name: 'Medium', value: data.incident_counts.medium, color: '#2196f3' },
    { name: 'Low', value: data.incident_counts.low, color: '#4caf50' },
  ] : [];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Security Incidents by Severity
      </Typography>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={incidentData}
            cx="50%"
            cy="50%"
            outerRadius={80}
            dataKey="value"
          >
            {incidentData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default SecurityMetrics;
