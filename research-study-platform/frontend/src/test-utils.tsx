import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider } from './contexts/AuthContext';

// Mock user data for testing
export const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  participant_id: 'P001',
  study_group: 'PDF',
  is_staff: false,
  is_superuser: false,
  study_completed: false,
};

export const mockAdmin = {
  id: 2,
  username: 'admin',
  email: 'admin@example.com',
  participant_id: 'A001',
  study_group: 'PDF',
  is_staff: true,
  is_superuser: true,
  study_completed: false,
};

// Mock study data
export const mockStudy = {
  id: 1,
  name: 'Test Study',
  description: 'A test study',
  created_by: 2,
  is_active: true,
  max_participants: 100,
  participant_count: 10,
  completion_rate: 75.0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

// Mock participant data
export const mockParticipant = {
  id: 1,
  user: mockUser,
  study: mockStudy,
  anonymized_id: 'P001_ABC123',
  assigned_group: 'PDF',
  consent_given: true,
  gdpr_consent: true,
  data_processing_consent: true,
  is_anonymized: false,
  withdrawn: false,
  created_at: '2024-01-01T00:00:00Z',
};

// Mock quiz data
export const mockQuizQuestion = {
  id: 'q1',
  question_text: 'What command lists files in Linux?',
  question_type: 'multiple_choice',
  is_required: true,
  points: 10,
  choices: [
    { id: 'a1', text: 'ls', is_correct: true },
    { id: 'a2', text: 'dir', is_correct: false },
    { id: 'a3', text: 'list', is_correct: false },
    { id: 'a4', text: 'files', is_correct: false },
  ],
};

export const mockQuiz = {
  id: 'pre_assessment',
  title: 'Pre-Assessment',
  description: 'Test your knowledge',
  quiz_type: 'pre_assessment',
  time_limit_minutes: 15,
  questions: [mockQuizQuestion],
  can_retake: false,
  max_attempts: 1,
};

interface AllTheProvidersProps {
  children: React.ReactNode;
  initialUser?: any;
  initialRoute?: string;
}

// Create providers wrapper for testing
const AllTheProviders: React.FC<AllTheProvidersProps> = ({ 
  children, 
  initialUser = null,
  initialRoute = '/' 
}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
    },
  });

  // Mock the AuthContext value
  const authContextValue = {
    user: initialUser,
    login: jest.fn(),
    logout: jest.fn(),
    updateUser: jest.fn(),
    isLoading: false,
    token: initialUser ? 'mock-token' : null,
  };

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

// Custom render function that includes providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & {
    initialUser?: any;
    initialRoute?: string;
  }
) => {
  const { initialUser, initialRoute, ...renderOptions } = options || {};
  
  return render(ui, {
    wrapper: ({ children }) => (
      <AllTheProviders initialUser={initialUser} initialRoute={initialRoute}>
        {children}
      </AllTheProviders>
    ),
    ...renderOptions,
  });
};

// Helper function to create a mock event
export const createMockEvent = (eventType: string, target: any = {}) => {
  return {
    type: eventType,
    target: { value: '', ...target },
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
    currentTarget: target,
  };
};

// Helper function to wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0));

// Helper function to create mock file
export const createMockFile = (name: string, size: number, type: string) => {
  const file = new File([''], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

// Helper function to mock localStorage
export const mockLocalStorage = () => {
  const store: { [key: string]: string } = {};
  
  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
  };
};

// Helper function to mock API responses
export const mockApiResponse = (data: any, status: number = 200) => {
  return Promise.resolve({
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {},
  });
};

// Helper function to mock API error
export const mockApiError = (message: string, status: number = 500) => {
  const error = new Error(message);
  (error as any).response = {
    status,
    statusText: 'Error',
    data: { error: message },
  };
  return Promise.reject(error);
};

// Helper function to simulate user interaction delays
export const simulateUserDelay = (ms: number = 100) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Re-export everything
export * from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
export { customRender as render };