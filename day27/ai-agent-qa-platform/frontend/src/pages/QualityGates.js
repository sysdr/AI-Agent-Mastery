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

const ValidationForm = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 30px;
`;

const SectionGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
`;

const Section = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 16px;
  border-radius: 8px;
`;

const CheckboxGroup = styled.div`
  margin-bottom: 12px;
`;

const Checkbox = styled.input`
  margin-right: 8px;
`;

const Label = styled.label`
  color: white;
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
  margin-top: 4px;

  &::placeholder {
    color: rgba(255, 255, 255, 0.6);
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
  width: 100%;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 255, 136, 0.3);
  }
`;

const ResultsContainer = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const GateResult = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border-left: 4px solid ${props => props.status === 'passed' ? '#00ff88' : '#ff4444'};
`;

const QualityGates = () => {
  const [deploymentData, setDeploymentData] = useState({
    security: {
      vulnerability_scan: { status: 'failed' },
      headers_configured: false,
      authentication: false,
      input_validation: false
    },
    performance: {
      avg_response_time_ms: 300,
      error_rate: 0.02,
      requests_per_second: 80,
      cpu_usage: 0.9
    },
    compliance: {
      gdpr_assessment: { compliant: false },
      soc2_controls: { implemented: false },
      audit_logging: false,
      encryption: { enabled: false }
    },
    ai_ethics: {
      bias_testing: { completed: false },
      explainability: false,
      human_oversight: false,
      fairness_score: 0.6
    }
  });
  
  const [validating, setValidating] = useState(false);
  const [validationResults, setValidationResults] = useState(null);

  const runValidation = async () => {
    setValidating(true);
    try {
      const response = await axios.post('/quality-gates/validate', deploymentData);
      setValidationResults(response.data);
    } catch (error) {
      console.error('Error running validation:', error);
    }
    setValidating(false);
  };

  const updateSecurityData = (field, value) => {
    setDeploymentData({
      ...deploymentData,
      security: {
        ...deploymentData.security,
        [field]: field === 'vulnerability_scan' ? { status: value ? 'passed' : 'failed' } : value
      }
    });
  };

  const updatePerformanceData = (field, value) => {
    setDeploymentData({
      ...deploymentData,
      performance: {
        ...deploymentData.performance,
        [field]: parseFloat(value) || value
      }
    });
  };

  return (
    <Container>
      <Header>Quality Gates Validation</Header>
      
      <ValidationForm>
        <h3 style={{ color: 'white', marginTop: 0 }}>Configure Deployment Parameters</h3>
        
        <SectionGrid>
          <Section>
            <h4 style={{ color: '#00ff88', marginTop: 0 }}>Security Settings</h4>
            <CheckboxGroup>
              <Checkbox 
                type="checkbox" 
                checked={deploymentData.security.vulnerability_scan.status === 'passed'}
                onChange={(e) => updateSecurityData('vulnerability_scan', e.target.checked)}
              />
              <Label>Vulnerability Scan Passed</Label>
            </CheckboxGroup>
            <CheckboxGroup>
              <Checkbox 
                type="checkbox"
                checked={deploymentData.security.headers_configured}
                onChange={(e) => updateSecurityData('headers_configured', e.target.checked)}
              />
              <Label>Security Headers Configured</Label>
            </CheckboxGroup>
            <CheckboxGroup>
              <Checkbox 
                type="checkbox"
                checked={deploymentData.security.authentication}
                onChange={(e) => updateSecurityData('authentication', e.target.checked)}
              />
              <Label>Authentication Enabled</Label>
            </CheckboxGroup>
            <CheckboxGroup>
              <Checkbox 
                type="checkbox"
                checked={deploymentData.security.input_validation}
                onChange={(e) => updateSecurityData('input_validation', e.target.checked)}
              />
              <Label>Input Validation Implemented</Label>
            </CheckboxGroup>
          </Section>

          <Section>
            <h4 style={{ color: '#00ff88', marginTop: 0 }}>Performance Metrics</h4>
            <div style={{ marginBottom: '12px' }}>
              <Label>Average Response Time (ms)</Label>
              <Input 
                type="number"
                value={deploymentData.performance.avg_response_time_ms}
                onChange={(e) => updatePerformanceData('avg_response_time_ms', e.target.value)}
              />
            </div>
            <div style={{ marginBottom: '12px' }}>
              <Label>Error Rate (0.0-1.0)</Label>
              <Input 
                type="number"
                step="0.001"
                value={deploymentData.performance.error_rate}
                onChange={(e) => updatePerformanceData('error_rate', e.target.value)}
              />
            </div>
            <div style={{ marginBottom: '12px' }}>
              <Label>Requests Per Second</Label>
              <Input 
                type="number"
                value={deploymentData.performance.requests_per_second}
                onChange={(e) => updatePerformanceData('requests_per_second', e.target.value)}
              />
            </div>
          </Section>
        </SectionGrid>

        <Button onClick={runValidation} disabled={validating}>
          {validating ? 'Validating Quality Gates...' : 'Run Quality Gate Validation'}
        </Button>
      </ValidationForm>

      {validationResults && (
        <ResultsContainer>
          <h3 style={{ color: 'white', marginTop: 0 }}>
            Validation Results - Overall Status: 
            <span style={{ color: validationResults.overall_status === 'passed' ? '#00ff88' : '#ff4444', marginLeft: '8px' }}>
              {validationResults.overall_status.toUpperCase()}
            </span>
          </h3>
          
          <div style={{ color: 'white', marginBottom: '20px' }}>
            Compliance Score: {validationResults.compliance_score}% | 
            Gates Passed: {validationResults.gates_passed} | 
            Gates Failed: {validationResults.gates_failed}
          </div>

          {Object.entries(validationResults.gate_results).map(([gateName, result]) => (
            <GateResult key={gateName} status={result.status}>
              <h4 style={{ color: 'white', marginTop: 0, textTransform: 'capitalize' }}>
                {gateName.replace('_', ' ')} Gate - {result.status.toUpperCase()}
              </h4>
              <div style={{ color: 'rgba(255,255,255,0.8)', marginBottom: '8px' }}>
                Score: {(result.score * 100).toFixed(0)}%
              </div>
              <div style={{ color: 'rgba(255,255,255,0.7)' }}>
                {result.details}
              </div>
            </GateResult>
          ))}

          {validationResults.recommendations?.length > 0 && (
            <div style={{ marginTop: '20px', padding: '16px', background: 'rgba(255,136,0,0.1)', borderRadius: '8px' }}>
              <h4 style={{ color: '#ff8800', marginTop: 0 }}>Recommendations</h4>
              <ul style={{ color: 'white', paddingLeft: '20px' }}>
                {validationResults.recommendations.map((rec, index) => (
                  <li key={index} style={{ marginBottom: '8px' }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </ResultsContainer>
      )}
    </Container>
  );
};

export default QualityGates;
