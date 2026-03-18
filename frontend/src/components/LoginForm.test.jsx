import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import LoginForm from './LoginForm';

// Mock fetch
global.fetch = jest.fn();

describe('LoginForm', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders login form with all elements', () => {
    const mockOnLogin = jest.fn();
    render(<LoginForm onLogin={mockOnLogin} />);

    // Check that all elements are in the document
    expect(screen.getByText(/Login/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByTestId('login-button')).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    const mockOnLogin = jest.fn();
    render(<LoginForm onLogin={mockOnLogin} />);

    // Submit the form without filling any fields
    fireEvent.click(screen.getByTestId('login-button'));

    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/Username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/Password is required/i)).toBeInTheDocument();
    });

    // Ensure the onLogin function wasn't called
    expect(mockOnLogin).not.toHaveBeenCalled();
  });

  test('shows validation error for short password', async () => {
    const mockOnLogin = jest.fn();
    render(<LoginForm onLogin={mockOnLogin} />);

    // Fill username but use a short password
    fireEvent.change(screen.getByTestId('username-input'), {
      target: { name: 'username', value: 'testuser' }
    });
    fireEvent.change(screen.getByTestId('password-input'), {
      target: { name: 'password', value: '12345' }
    });

    // Submit the form
    fireEvent.click(screen.getByTestId('login-button'));

    // Check for password validation error
    await waitFor(() => {
      expect(screen.getByText(/Password must be at least 6 characters/i)).toBeInTheDocument();
    });

    // Ensure the onLogin function wasn't called
    expect(mockOnLogin).not.toHaveBeenCalled();
  });

  test('handles successful login', async () => {
    // Mock a successful response
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ access_token: 'fake-token', token_type: 'bearer' })
    });

    const mockOnLogin = jest.fn();
    render(<LoginForm onLogin={mockOnLogin} />);

    // Fill in valid credentials
    fireEvent.change(screen.getByTestId('username-input'), {
      target: { name: 'username', value: 'testuser' }
    });
    fireEvent.change(screen.getByTestId('password-input'), {
      target: { name: 'password', value: 'password123' }
    });

    // Submit the form
    fireEvent.click(screen.getByTestId('login-button'));

    // Verify the fetch was called with correct parameters
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/token', expect.any(Object));
      expect(mockOnLogin).toHaveBeenCalledWith(expect.objectContaining({
        username: 'testuser',
        token: 'fake-token'
      }));
    });
  });

  test('handles failed login', async () => {
    // Mock a failed response
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Invalid credentials' })
    });

    const mockOnLogin = jest.fn();
    render(<LoginForm onLogin={mockOnLogin} />);

    // Fill in invalid credentials
    fireEvent.change(screen.getByTestId('username-input'), {
      target: { name: 'username', value: 'wronguser' }
    });
    fireEvent.change(screen.getByTestId('password-input'), {
      target: { name: 'password', value: 'wrongpassword' }
    });

    // Submit the form
    fireEvent.click(screen.getByTestId('login-button'));

    // Verify error message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
      expect(mockOnLogin).not.toHaveBeenCalled();
    });
  });
});
