import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Dashboard from './Dashboard';

const mockNetworkData = {
  agents: {
    agent_1: {
      id: 'agent_1',
      status: 'active',
      reputation: 1.2,
      resource_usage: { api_calls: 5, cpu: 0.1, memory: 0.05 },
      port: 8001
    }
  },
  connections: 2,
  total_messages: 10,
  network_health: 'healthy',
  resource_pool: {
    total_cpu: 0.1,
    total_api_calls: 5,
    available_api_credits: 995
  }
};

test('renders dashboard with network data', () => {
  render(<Dashboard networkData={mockNetworkData} onSolveProblem={() => {}} />);
  
  expect(screen.getByText('1')).toBeInTheDocument(); // Active agents
  expect(screen.getByText('Active Agents')).toBeInTheDocument();
  expect(screen.getByText('healthy')).toBeInTheDocument();
});

test('handles problem solving', async () => {
  const mockSolveProblem = jest.fn().mockResolvedValue({
    problem: 'Test problem',
    consensus_solution: 'Test solution',
    confidence: 0.95,
    participating_agents: 1
  });

  render(<Dashboard networkData={mockNetworkData} onSolveProblem={mockSolveProblem} />);
  
  const textarea = screen.getByPlaceholderText(/Enter a problem/);
  const button = screen.getByText(/Solve with Network/);
  
  fireEvent.change(textarea, { target: { value: 'Test problem' } });
  fireEvent.click(button);
  
  await waitFor(() => {
    expect(mockSolveProblem).toHaveBeenCalledWith('Test problem');
  });
});
