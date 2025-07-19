import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockUser } from '../../../test-utils';
import LoginForm from '../LoginForm';
import { toast } from 'react-hot-toast';

// Mock the auth context
const mockLogin = jest.fn();
jest.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    login: mockLogin,
    isLoading: false,
  }),
}));

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  Link: ({ children, to }: any) => <a href={to}>{children}</a>,
}));

describe('LoginForm', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form correctly', () => {
    render(<LoginForm />);
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByText('Linux Learning Study')).toBeInTheDocument();
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });

  it('displays form validation errors for empty fields', async () => {
    render(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    await user.click(submitButton);
    
    expect(screen.getByText('Username is required')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
  });

  it('validates minimum password length', async () => {
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'testuser');
    await user.type(passwordInput, '123'); // Less than 6 characters
    await user.click(submitButton);
    
    expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
  });

  it('validates participant ID format', async () => {
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'invalid-id'); // Invalid format
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    expect(screen.getByText('Invalid participant ID format')).toBeInTheDocument();
  });

  it('accepts valid participant ID formats', async () => {
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    // Test valid formats
    const validIds = ['P001', 'A001', 'R001', 'T001'];
    
    for (const id of validIds) {
      await user.clear(usernameInput);
      await user.clear(passwordInput);
      await user.type(usernameInput, id);
      await user.type(passwordInput, 'password123');
      
      // Should not show validation error
      expect(screen.queryByText('Invalid participant ID format')).not.toBeInTheDocument();
    }
  });

  it('submits form with valid credentials', async () => {
    mockLogin.mockResolvedValue({ success: true });
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('P001', 'password123');
    });
  });

  it('handles login success correctly', async () => {
    mockLogin.mockResolvedValue({ success: true });
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Welcome back!');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('handles login failure correctly', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Invalid credentials. Please check your participant ID and password.');
    });
  });

  it('shows loading state during login', async () => {
    let resolveLogin: (value: any) => void;
    const loginPromise = new Promise(resolve => {
      resolveLogin = resolve;
    });
    mockLogin.mockReturnValue(loginPromise);
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    // Should show loading state
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    
    // Resolve the promise
    resolveLogin!({ success: true });
    
    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('prevents multiple submissions', async () => {
    let resolveLogin: (value: any) => void;
    const loginPromise = new Promise(resolve => {
      resolveLogin = resolve;
    });
    mockLogin.mockReturnValue(loginPromise);
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'password123');
    
    // Click submit multiple times
    await user.click(submitButton);
    await user.click(submitButton);
    await user.click(submitButton);
    
    // Should only call login once
    expect(mockLogin).toHaveBeenCalledTimes(1);
    
    resolveLogin!({ success: true });
  });

  it('handles keyboard navigation correctly', async () => {
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    // Tab through form
    await user.tab();
    expect(usernameInput).toHaveFocus();
    
    await user.tab();
    expect(passwordInput).toHaveFocus();
    
    await user.tab();
    expect(submitButton).toHaveFocus();
  });

  it('submits form on Enter key press', async () => {
    mockLogin.mockResolvedValue({ success: true });
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'password123');
    await user.keyboard('{Enter}');
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('P001', 'password123');
    });
  });

  it('clears validation errors when user types', async () => {
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    // Trigger validation errors
    await user.click(submitButton);
    expect(screen.getByText('Username is required')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
    
    // Start typing in username
    await user.type(usernameInput, 'P');
    expect(screen.queryByText('Username is required')).not.toBeInTheDocument();
    
    // Start typing in password
    await user.type(passwordInput, 'p');
    expect(screen.queryByText('Password is required')).not.toBeInTheDocument();
  });

  it('shows password visibility toggle', async () => {
    render(<LoginForm />);
    
    const passwordInput = screen.getByLabelText('Password');
    const toggleButton = screen.getByRole('button', { name: /show password/i });
    
    // Initially password should be hidden
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle to show password
    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle to hide password again
    await user.click(toggleButton);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('handles network errors gracefully', async () => {
    mockLogin.mockRejectedValue(new Error('Network Error'));
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'password123');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Network error. Please check your connection and try again.');
    });
  });

  it('preserves form data on failed login', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));
    
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    await user.type(usernameInput, 'P001');
    await user.type(passwordInput, 'wrongpassword');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
    
    // Form data should be preserved
    expect(usernameInput).toHaveValue('P001');
    expect(passwordInput).toHaveValue('wrongpassword');
  });

  it('displays appropriate error messages for different error types', async () => {
    const errorCases = [
      { error: 'Invalid credentials', expectedMessage: 'Invalid credentials. Please check your participant ID and password.' },
      { error: 'Account locked', expectedMessage: 'Your account has been locked. Please contact the administrator.' },
      { error: 'Network Error', expectedMessage: 'Network error. Please check your connection and try again.' },
    ];
    
    for (const { error, expectedMessage } of errorCases) {
      mockLogin.mockRejectedValue(new Error(error));
      
      render(<LoginForm />);
      
      const usernameInput = screen.getByLabelText('Username');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });
      
      await user.type(usernameInput, 'P001');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(toast.error).toHaveBeenCalledWith(expectedMessage);
      });
      
      // Clear for next test
      jest.clearAllMocks();
    }
  });

  it('has proper accessibility attributes', () => {
    render(<LoginForm />);
    
    const usernameInput = screen.getByLabelText('Username');
    const passwordInput = screen.getByLabelText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    expect(usernameInput).toHaveAttribute('aria-required', 'true');
    expect(passwordInput).toHaveAttribute('aria-required', 'true');
    expect(submitButton).toHaveAttribute('type', 'submit');
  });
});