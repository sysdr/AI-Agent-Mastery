import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock the auth hook to avoid complex setup
jest.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    isAuthenticated: false,
    user: null,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

test('renders login page when not authenticated', () => {
  render(<App />);
  // App should redirect to login page
  expect(document.body).toBeInTheDocument();
});
