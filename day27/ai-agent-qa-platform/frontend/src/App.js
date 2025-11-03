import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Dashboard from './pages/Dashboard';
import SecurityScans from './pages/SecurityScans';
import LoadTesting from './pages/LoadTesting';
import QualityGates from './pages/QualityGates';
import Navigation from './components/Navigation';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
`;

const ContentArea = styled.div`
  margin-left: 250px;
  padding: 20px;
  min-height: 100vh;
`;

function App() {
  return (
    <AppContainer>
      <Router>
        <Navigation />
        <ContentArea>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/security" element={<SecurityScans />} />
            <Route path="/load-testing" element={<LoadTesting />} />
            <Route path="/quality-gates" element={<QualityGates />} />
          </Routes>
        </ContentArea>
      </Router>
    </AppContainer>
  );
}

export default App;
