import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from './App';

test('renders AI Agent Self-Healing System header', () => {
  render(<App />);
  const headerElement = screen.getByText(/AI Agent Self-Healing System/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders navigation tabs', () => {
  render(<App />);
  const healthTab = screen.getByText(/System Health/i);
  const securityTab = screen.getByText(/Security Monitor/i);
  const incidentsTab = screen.getByText(/Incidents/i);
  const metricsTab = screen.getByText(/Metrics/i);
  
  expect(healthTab).toBeInTheDocument();
  expect(securityTab).toBeInTheDocument();
  expect(incidentsTab).toBeInTheDocument();
  expect(metricsTab).toBeInTheDocument();
});
