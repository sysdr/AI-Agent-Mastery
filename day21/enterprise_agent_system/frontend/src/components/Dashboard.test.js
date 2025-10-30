import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Mock WebSocket hook
jest.mock('../hooks/useWebSocket', () => ({
  useWebSocket: () => ({
    isConnected: true,
    lastMessage: null
  })
}));

test('renders dashboard header', () => {
  render(
    <BrowserRouter>
      <Dashboard />
    </BrowserRouter>
  );
  
  const headerElement = screen.getByText(/Enterprise Agent Dashboard/i);
  expect(headerElement).toBeInTheDocument();
});
