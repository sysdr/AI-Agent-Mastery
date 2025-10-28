import React from 'react';
import { Typography, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import { useQuery } from 'react-query';
import axios from 'axios';

const RecentIncidents: React.FC = () => {
  const { data: incidents } = useQuery(
    'recent-incidents',
    () => axios.get('http://localhost:8000/security/incidents?limit=10').then(res => res.data)
  );

  return (
    <div>
      <Typography variant="h6" gutterBottom>
        Recent Security Incidents
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Type</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Created</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {incidents?.map((incident: any) => (
            <TableRow key={incident.id}>
              <TableCell>{incident.incident_type}</TableCell>
              <TableCell>{incident.severity}</TableCell>
              <TableCell>{incident.status}</TableCell>
              <TableCell>{new Date(incident.created_at).toLocaleString()}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default RecentIncidents;
