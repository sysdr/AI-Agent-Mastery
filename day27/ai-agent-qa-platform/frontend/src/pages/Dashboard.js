import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const DashboardContainer = styled.div`
  padding: 20px;
`;

const Header = styled.h1`
  color: white;
  margin-bottom: 30px;
  font-size: 2.5rem;
  font-weight: 700;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const MetricCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
`;

const MetricTitle = styled.h3`
  color: white;
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  font-weight: 600;
`;

const MetricValue = styled.div`
  color: #00ff88;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
`;

const MetricSubtext = styled.div`
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
`;

const ChartContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
  margin-bottom: 20px;
`;

const AlertsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
`;

const Alert = styled.div`
  background: rgba(255, 0, 0, 0.1);
  border-left: 4px solid #ff4444;
  padding: 12px 16px;
  margin-bottom: 12px;
  border-radius: 4px;
  color: white;
`;

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await axios.get('/metrics/dashboard');
        setDashboardData(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setLoading(false);
      }
    };

    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <DashboardContainer>
        <Header>Loading Dashboard...</Header>
      </DashboardContainer>
    );
  }

  const securityMetrics = dashboardData?.metrics?.security_metrics || {};
  const performanceMetrics = dashboardData?.metrics?.performance_metrics || {};
  const complianceMetrics = dashboardData?.metrics?.compliance_metrics || {};
  const qualityGatesMetrics = dashboardData?.metrics?.quality_gates_metrics || {};

  const responseTimeData = [
    { name: 'Hour 1', time: performanceMetrics.avg_response_time_ms * 0.8 },
    { name: 'Hour 2', time: performanceMetrics.avg_response_time_ms * 0.9 },
    { name: 'Hour 3', time: performanceMetrics.avg_response_time_ms * 1.1 },
    { name: 'Hour 4', time: performanceMetrics.avg_response_time_ms },
  ];

  const vulnerabilityData = [
    { name: 'Critical', value: securityMetrics.critical_vulnerabilities, color: '#ff4444' },
    { name: 'High', value: securityMetrics.high_vulnerabilities, color: '#ff8800' },
    { name: 'Medium', value: securityMetrics.medium_vulnerabilities, color: '#ffbb00' },
    { name: 'Low', value: securityMetrics.low_vulnerabilities, color: '#00ff88' },
  ];

  return (
    <DashboardContainer>
      <Header>QA Automation Dashboard</Header>
      
      <MetricsGrid>
        <MetricCard>
          <MetricTitle>Security Score</MetricTitle>
          <MetricValue>{securityMetrics.security_score}/10</MetricValue>
          <MetricSubtext>Threat detection rate: {(securityMetrics.threat_detection_rate * 100).toFixed(1)}%</MetricSubtext>
        </MetricCard>
        
        <MetricCard>
          <MetricTitle>Response Time</MetricTitle>
          <MetricValue>{performanceMetrics.avg_response_time_ms}ms</MetricValue>
          <MetricSubtext>RPS: {performanceMetrics.requests_per_second}</MetricSubtext>
        </MetricCard>
        
        <MetricCard>
          <MetricTitle>Compliance Score</MetricTitle>
          <MetricValue>{(complianceMetrics.gdpr_compliance_score * 100).toFixed(0)}%</MetricValue>
          <MetricSubtext>Controls implemented: {complianceMetrics.soc2_controls_implemented}%</MetricSubtext>
        </MetricCard>
        
        <MetricCard>
          <MetricTitle>Quality Gates</MetricTitle>
          <MetricValue>{(qualityGatesMetrics.overall_pass_rate * 100).toFixed(0)}%</MetricValue>
          <MetricSubtext>Deployments today: {qualityGatesMetrics.deployments_today}</MetricSubtext>
        </MetricCard>
      </MetricsGrid>

      <ChartContainer>
        <MetricTitle>Response Time Trend</MetricTitle>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={responseTimeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="name" stroke="rgba(255,255,255,0.7)" />
            <YAxis stroke="rgba(255,255,255,0.7)" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.8)', 
                border: 'none',
                borderRadius: '8px',
                color: 'white'
              }} 
            />
            <Line type="monotone" dataKey="time" stroke="#00ff88" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <ChartContainer>
          <MetricTitle>Vulnerability Distribution</MetricTitle>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={vulnerabilityData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {vulnerabilityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartContainer>

        <AlertsContainer>
          <MetricTitle>System Alerts</MetricTitle>
          {dashboardData?.alerts?.length > 0 ? (
            dashboardData.alerts.map((alert, index) => (
              <Alert key={index}>
                <strong>{alert.severity.toUpperCase()}</strong>: {alert.message}
              </Alert>
            ))
          ) : (
            <div style={{ color: '#00ff88' }}>No active alerts</div>
          )}
        </AlertsContainer>
      </div>
    </DashboardContainer>
  );
};

export default Dashboard;
