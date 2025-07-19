import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockAdmin, mockUser } from '../../../test-utils';
import AdminDashboard from '../AdminDashboard';

// Mock the sub-components
jest.mock('../ParticipantManager', () => {
  return function MockParticipantManager() {
    return <div data-testid="participant-manager">Participant Manager</div>;
  };
});

jest.mock('../SessionMonitor', () => {
  return function MockSessionMonitor() {
    return <div data-testid="session-monitor">Session Monitor</div>;
  };
});

jest.mock('../AnalyticsDashboard', () => {
  return function MockAnalyticsDashboard() {
    return <div data-testid="analytics-dashboard">Analytics Dashboard</div>;
  };
});

jest.mock('../DataExport', () => {
  return function MockDataExport() {
    return <div data-testid="data-export">Data Export</div>;
  };
});

jest.mock('../PrivacyCompliance', () => {
  return function MockPrivacyCompliance() {
    return <div data-testid="privacy-compliance">Privacy Compliance</div>;
  };
});

jest.mock('../ResearchUtilities', () => {
  return function MockResearchUtilities() {
    return <div data-testid="research-utilities">Research Utilities</div>;
  };
});

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('AdminDashboard', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(<AdminDashboard />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('redirects non-admin users to dashboard', async () => {
    render(<AdminDashboard />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('renders admin dashboard for admin users', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Linux Learning Study - Administrative Interface')).toBeInTheDocument();
    expect(screen.getByText('Logged in as: admin (Researcher)')).toBeInTheDocument();
  });

  it('renders all navigation tabs', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    const expectedTabs = [
      'Participants',
      'Sessions',
      'Analytics',
      'Data Export',
      'Privacy',
      'Utilities'
    ];

    expectedTabs.forEach(tabName => {
      expect(screen.getByText(tabName)).toBeInTheDocument();
    });
  });

  it('shows participants tab by default', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByTestId('participant-manager')).toBeInTheDocument();
    });
  });

  it('switches between tabs correctly', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    // Click on Analytics tab
    await user.click(screen.getByText('Analytics'));
    expect(screen.getByTestId('analytics-dashboard')).toBeInTheDocument();

    // Click on Data Export tab
    await user.click(screen.getByText('Data Export'));
    expect(screen.getByTestId('data-export')).toBeInTheDocument();

    // Click on Privacy tab
    await user.click(screen.getByText('Privacy'));
    expect(screen.getByTestId('privacy-compliance')).toBeInTheDocument();

    // Click on Utilities tab
    await user.click(screen.getByText('Utilities'));
    expect(screen.getByTestId('research-utilities')).toBeInTheDocument();

    // Click on Sessions tab
    await user.click(screen.getByText('Sessions'));
    expect(screen.getByTestId('session-monitor')).toBeInTheDocument();
  });

  it('highlights active tab correctly', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    const participantsTab = screen.getByText('Participants').closest('button');
    expect(participantsTab).toHaveClass('border-primary-500', 'text-primary-600');

    // Switch to analytics tab
    await user.click(screen.getByText('Analytics'));
    
    const analyticsTab = screen.getByText('Analytics').closest('button');
    expect(analyticsTab).toHaveClass('border-primary-500', 'text-primary-600');
    
    // Participants tab should no longer be highlighted
    expect(participantsTab).not.toHaveClass('border-primary-500', 'text-primary-600');
  });

  it('shows tab descriptions correctly', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    // Default description for participants tab
    expect(screen.getByText('Manage participants and group assignments')).toBeInTheDocument();

    // Switch to analytics and check description
    await user.click(screen.getByText('Analytics'));
    expect(screen.getByText('View study statistics and performance')).toBeInTheDocument();

    // Switch to export and check description
    await user.click(screen.getByText('Data Export'));
    expect(screen.getByText('Export data for analysis')).toBeInTheDocument();
  });

  it('handles superuser access correctly', async () => {
    const superUser = { ...mockAdmin, is_superuser: true };
    render(<AdminDashboard />, { initialUser: superUser });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('handles staff user access correctly', async () => {
    const staffUser = { ...mockUser, is_staff: true };
    render(<AdminDashboard />, { initialUser: staffUser });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('renders with correct CSS classes and structure', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    const container = screen.getByText('Research Dashboard').closest('.min-h-screen');
    expect(container).toHaveClass('bg-gray-50');

    const headerSection = screen.getByText('Research Dashboard').closest('.bg-white');
    expect(headerSection).toHaveClass('rounded-lg', 'shadow-lg');
  });

  it('displays user information correctly', async () => {
    render(<AdminDashboard />, { initialUser: mockAdmin });
    
    await waitFor(() => {
      expect(screen.getByText('Research Dashboard')).toBeInTheDocument();
    });

    expect(screen.getByText('Logged in as: admin (Researcher)')).toBeInTheDocument();
  });

  it('handles null user gracefully', async () => {
    render(<AdminDashboard />, { initialUser: null });
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('handles regular user without staff privileges', async () => {
    const regularUser = { ...mockUser, is_staff: false, is_superuser: false };
    render(<AdminDashboard />, { initialUser: regularUser });
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });
});