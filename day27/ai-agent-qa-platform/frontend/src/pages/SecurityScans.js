import React, { useState, useEffect } from 'react';
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

const ScanForm = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 30px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 16px;
  margin-bottom: 16px;

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

const ScanResults = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 20px;
`;

const VulnerabilityItem = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 4px solid ${props => {
    switch(props.severity) {
      case 'critical': return '#ff4444';
      case 'high': return '#ff8800';
      case 'medium': return '#ffbb00';
      default: return '#00ff88';
    }
  }};
`;

const SecurityScans = () => {
  const [targetUrl, setTargetUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [scanResults, setScanResults] = useState(null);
  const [scanId, setScanId] = useState(null);

  const startScan = async () => {
    if (!targetUrl) return;
    
    setScanning(true);
    try {
      const response = await axios.post('/security/scan', null, {
        params: { target_url: targetUrl }
      });
      setScanId(response.data.scan_id);
      
      // Poll for results
      pollScanResults(response.data.scan_id);
    } catch (error) {
      console.error('Error starting scan:', error);
      setScanning(false);
    }
  };

  const pollScanResults = (scanId) => {
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`/security/scan/${scanId}`);
        if (response.data.status === 'completed' || response.data.status === 'failed') {
          setScanResults(response.data);
          setScanning(false);
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Error polling scan results:', error);
      }
    }, 2000);
  };

  return (
    <Container>
      <Header>Security Vulnerability Scanning</Header>
      
      <ScanForm>
        <h3 style={{ color: 'white', marginTop: 0 }}>Start New Security Scan</h3>
        <Input
          type="url"
          placeholder="Enter target URL (e.g., https://your-ai-agent.com)"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
        />
        <Button onClick={startScan} disabled={scanning}>
          {scanning ? 'Scanning...' : 'Start Security Scan'}
        </Button>
      </ScanForm>

      {scanResults && (
        <ScanResults>
          <h3 style={{ color: 'white', marginTop: 0 }}>
            Scan Results - Risk Score: {scanResults.risk_score?.toFixed(1)}/10
          </h3>
          <div style={{ color: 'rgba(255,255,255,0.8)', marginBottom: '20px' }}>
            Status: <span style={{ color: scanResults.status === 'completed' ? '#00ff88' : '#ff4444' }}>
              {scanResults.status}
            </span>
          </div>

          {scanResults.vulnerabilities?.map((vuln, index) => (
            <VulnerabilityItem key={index} severity={vuln.severity}>
              <div style={{ color: 'white', fontWeight: 'bold', marginBottom: '8px' }}>
                {vuln.type.replace('_', ' ').toUpperCase()} - {vuln.severity.toUpperCase()}
              </div>
              <div style={{ color: 'rgba(255,255,255,0.9)', marginBottom: '8px' }}>
                {vuln.description}
              </div>
              <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>
                CVSS Score: {vuln.cvss_score} | Remediation: {vuln.remediation}
              </div>
            </VulnerabilityItem>
          ))}

          {scanResults.ai_analysis && (
            <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(0,255,136,0.1)', borderRadius: '8px' }}>
              <h4 style={{ color: '#00ff88', marginTop: 0 }}>AI Security Analysis</h4>
              <div style={{ color: 'white', whiteSpace: 'pre-wrap' }}>
                {scanResults.ai_analysis.analysis}
              </div>
            </div>
          )}
        </ScanResults>
      )}
    </Container>
  );
};

export default SecurityScans;
