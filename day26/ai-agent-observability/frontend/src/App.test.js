import { render, screen } from '@testing-library/react';
import App from './App';

test('renders observability dashboard', () => {
  render(<App />);
  const linkElement = screen.getByText(/observability/i);
  expect(linkElement).toBeInTheDocument();
});
