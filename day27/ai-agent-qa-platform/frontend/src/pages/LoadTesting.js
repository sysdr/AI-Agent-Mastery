import React, { useState } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const Container = styled.div`
  padding: 20px;
`;

const Header = styled.h1`
  color: white;
  margin-bottom: 30px;
  font-size: 2.5rem;
  font-weight: 700;
`;

const TestForm = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 30px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
`;

const Input = styled.input`
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 16px;

  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
  }

  &:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.2);
  }
`;

const Button = styled.button`
  background: linear-gradient(45deg, #00ff88, #00cc6a);
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 255, 136, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ResultsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const MetricRow = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
`;

const MetricCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 16px;
  border-radius: 8px;
  text-align: center;
`;

const LoadTesting = () => {
  const [testConfig, setTestConfig] = useState({
    targetUrl: '',
    users: 50,
    duration: 60
  });
  const [testing, setTesting] = useState(false);
  const [testResults, setTestResults] = useState(null);

  const startLoadTest = async () => {
    if (!testConfig.targetUrl) return;
    
    setTesting(true);
    try {
      const response = await axios.post('/load-test/start', null, {
        params: {
          target_url: testConfig.targetUrl,
          users: testConfig.users,
          duration: testConfig.duration
        }
      });
      
      // Poll for results
      pollTestResults(response.data.test_id);
    } catch (error) {
      console.error('Error starting load test:', error);
      setTesting(false);
    }
  };

  const pollTestResults = (testId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/load-test/${testId}`);
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          setTestResults(response.data);
          setTesting(false);
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error polling test results:', error);
      }
    }, 3000);
  };

  return (
    <Container>
      <Header>Load Testing & Attack Simulation</Header>
      
      <TestForm>
        <h3 style={{ color: 'white', marginTop: 0 }}>Configure Load Test</h3>
        <Input
          type="url"
          placeholder="Target URL"
          value={testConfig.targetUrl}
          onChange={(e) => setTestConfig({...testConfig, targetUrl: e.target.value})}
          style={{ width: '100%', marginBottom: '16px' }}
        />
        <FormGrid>
          <Input
            type="number"
            placeholder="Concurrent Users"
            value={testConfig.users}
            onChange={(e) => setTestConfig({...testConfig, users: parseInt(e.target.value)})}
          />
          <Input
            type="number"
            placeholder="Duration (seconds)"
            value={testConfig.duration}
            onChange={(e) => setTestConfig({...testConfig, duration: parseInt(e.target.value)})}
          />
          <Button onClick={startLoadTest} disabled={testing}>
            {testing ? 'Testing...' : 'Start Load Test'}
          </Button>
        </FormGrid>
      </TestForm>

      {testResults && (
        <ResultsContainer>
          <h3 style={{ color: 'white', marginTop: 0 }}>
            Load Test Results
          </h3>
          <div style={{ color: 'rgba(255,255,255,0.8)', marginBottom: '20px' }}>
            Status: <span style={{ color: testResults.status === 'completed' ? '#00ff88' : '#ff4444' }}>
              {testResults.status}
            </span>
          </div>

          {testResults.results && (
            <>
              <MetricRow>
                <MetricCard>
                  <div style={{ color: '#00ff88', fontSize: '2rem', fontWeight: 'bold' }}>
                    {testResults.results.total_requests}
                  </div>
                  <div style={{ color: 'white' }}>Total Requests</div>
                </MetricCard>
                <MetricCard>
                  <div style={{ color: '#00ff88', fontSize: '2rem', fontWeight: 'bold' }}>
                    {testResults.results.avg_response_time_ms?.toFixed(0)}ms
                  </div>
                  <div style={{ color: 'white' }}>Avg Response Time</div>
                </MetricCard>
                <MetricCard>
                  <div style={{ color: testResults.results.error_rate > 0.05 ? '#ff4444' : '#00ff88', fontSize: '2rem', fontWeight: 'bold' }}>
                    {(testResults.results.error_rate * 100).toFixed(2)}%
                  </div>
                  <div style={{ color: 'white' }}>Error Rate</div>
                </MetricCard>
              </MetricRow>

              <h4 style={{ color: 'white', marginBottom: '16px' }}>Attack Simulation Results</h4>
              {Object.entries(testResults.results.attack_results || {}).map(([attack, result]) => (
                <div key={attack} style={{ 
                  background: 'rgba(255,255,255,0.05)', 
                  padding: '16px', 
                  borderRadius: '8px', 
                  marginBottom: '12px' 
                }}>
                  <h5 style={{ color: '#00ff88', marginTop: 0 }}>
                    {attack.replace('_', ' ').replace(/^\w/, c => c.toUpperCase())}
                  </h5>
                  <div style={{ color: 'white' }}>
                    {JSON.stringify(result, null, 2)}
                  </div>
                </div>
              ))}
            </>
          )}
        </ResultsContainer>
      )}
    </Container>
  );
};

export default LoadTesting;
