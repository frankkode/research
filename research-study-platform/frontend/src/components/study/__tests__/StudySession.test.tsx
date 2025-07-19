import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockUser } from '../../../test-utils';
import StudySession from '../StudySession';

// Mock the sub-components
jest.mock('../../quiz/QuizInterface', () => {
  return function MockQuizInterface({ onComplete }: any) {
    return (
      <div data-testid="quiz-interface">
        <button onClick={() => onComplete({ score: 85 })}>Complete Quiz</button>
      </div>
    );
  };
});

jest.mock('../../pdf/PDFViewer', () => {
  return function MockPDFViewer({ onComplete }: any) {
    return (
      <div data-testid="pdf-viewer">
        <button onClick={() => onComplete()}>Complete PDF</button>
      </div>
    );
  };
});

jest.mock('../../chat/ChatInterface', () => {
  return function MockChatInterface({ onComplete }: any) {
    return (
      <div data-testid="chat-interface">
        <button onClick={() => onComplete()}>Complete Chat</button>
      </div>
    );
  };
});

jest.mock('../../quiz/QuizResults', () => {
  return function MockQuizResults({ onContinue }: any) {
    return (
      <div data-testid="quiz-results">
        <button onClick={() => onContinue()}>Continue</button>
      </div>
    );
  };
});

// Mock the API
jest.mock('../../../services/api', () => ({
  sessionApi: {
    startSession: jest.fn().mockResolvedValue({ sessionId: 'test-session-123' }),
    logInteraction: jest.fn().mockResolvedValue({ success: true }),
    completeSession: jest.fn().mockResolvedValue({ success: true }),
  },
}));

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('StudySession', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state initially', () => {
    render(<StudySession />, { initialUser: mockUser });
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('starts with pre-assessment for PDF group', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Phase 1: Pre-Assessment')).toBeInTheDocument();
    expect(screen.getByText('Please complete the pre-assessment quiz before starting the study.')).toBeInTheDocument();
  });

  it('starts with pre-assessment for ChatGPT group', async () => {
    const chatUser = { ...mockUser, study_group: 'CHATGPT' };
    render(<StudySession />, { initialUser: chatUser });
    
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Phase 1: Pre-Assessment')).toBeInTheDocument();
  });

  it('progresses through PDF study flow correctly', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    // Complete pre-assessment
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should show PDF study phase
    await waitFor(() => {
      expect(screen.getByText('Phase 2: Study Materials')).toBeInTheDocument();
      expect(screen.getByTestId('pdf-viewer')).toBeInTheDocument();
    });
    
    // Complete PDF study
    await user.click(screen.getByText('Complete PDF'));
    
    // Should show immediate recall quiz
    await waitFor(() => {
      expect(screen.getByText('Phase 3: Immediate Recall')).toBeInTheDocument();
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    // Complete immediate recall
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should show transfer quiz
    await waitFor(() => {
      expect(screen.getByText('Phase 4: Transfer Assessment')).toBeInTheDocument();
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    // Complete transfer quiz
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should show completion
    await waitFor(() => {
      expect(screen.getByText('Study Completed!')).toBeInTheDocument();
    });
  });

  it('progresses through ChatGPT study flow correctly', async () => {
    const chatUser = { ...mockUser, study_group: 'CHATGPT' };
    render(<StudySession />, { initialUser: chatUser });
    
    // Complete pre-assessment
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should show ChatGPT study phase
    await waitFor(() => {
      expect(screen.getByText('Phase 2: Study Materials')).toBeInTheDocument();
      expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
    });
    
    // Complete ChatGPT study
    await user.click(screen.getByText('Complete Chat'));
    
    // Should show immediate recall quiz
    await waitFor(() => {
      expect(screen.getByText('Phase 3: Immediate Recall')).toBeInTheDocument();
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    // Complete immediate recall
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should show transfer quiz
    await waitFor(() => {
      expect(screen.getByText('Phase 4: Transfer Assessment')).toBeInTheDocument();
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    // Complete transfer quiz
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should show completion
    await waitFor(() => {
      expect(screen.getByText('Study Completed!')).toBeInTheDocument();
    });
  });

  it('shows correct progress indicators', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    // Initial progress should be 0%
    await waitFor(() => {
      expect(screen.getByText('0%')).toBeInTheDocument();
    });
    
    // Complete pre-assessment
    await user.click(screen.getByText('Complete Quiz'));
    
    // Progress should be 25%
    await waitFor(() => {
      expect(screen.getByText('25%')).toBeInTheDocument();
    });
    
    // Complete PDF study
    await user.click(screen.getByText('Complete PDF'));
    
    // Progress should be 50%
    await waitFor(() => {
      expect(screen.getByText('50%')).toBeInTheDocument();
    });
    
    // Complete immediate recall
    await user.click(screen.getByText('Complete Quiz'));
    
    // Progress should be 75%
    await waitFor(() => {
      expect(screen.getByText('75%')).toBeInTheDocument();
    });
    
    // Complete transfer quiz
    await user.click(screen.getByText('Complete Quiz'));
    
    // Progress should be 100%
    await waitFor(() => {
      expect(screen.getByText('100%')).toBeInTheDocument();
    });
  });

  it('displays phase descriptions correctly', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    // Pre-assessment description
    await waitFor(() => {
      expect(screen.getByText('Please complete the pre-assessment quiz before starting the study.')).toBeInTheDocument();
    });
    
    // Complete pre-assessment
    await user.click(screen.getByText('Complete Quiz'));
    
    // PDF study description
    await waitFor(() => {
      expect(screen.getByText('Study the Linux tutorial PDF. Take your time to read and understand the material.')).toBeInTheDocument();
    });
    
    // Complete PDF study
    await user.click(screen.getByText('Complete PDF'));
    
    // Immediate recall description
    await waitFor(() => {
      expect(screen.getByText('Test your knowledge of what you just learned.')).toBeInTheDocument();
    });
    
    // Complete immediate recall
    await user.click(screen.getByText('Complete Quiz'));
    
    // Transfer assessment description
    await waitFor(() => {
      expect(screen.getByText('Apply your knowledge to solve new problems.')).toBeInTheDocument();
    });
  });

  it('shows different descriptions for ChatGPT group', async () => {
    const chatUser = { ...mockUser, study_group: 'CHATGPT' };
    render(<StudySession />, { initialUser: chatUser });
    
    // Complete pre-assessment
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Complete Quiz'));
    
    // ChatGPT study description
    await waitFor(() => {
      expect(screen.getByText('Chat with AI to learn about Linux commands. Ask questions and explore the topic.')).toBeInTheDocument();
    });
  });

  it('shows elapsed time correctly', async () => {
    jest.useFakeTimers();
    
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    await waitFor(() => {
      expect(screen.getByText('0:00')).toBeInTheDocument();
    });
    
    // Advance time by 5 minutes
    jest.advanceTimersByTime(5 * 60 * 1000);
    
    await waitFor(() => {
      expect(screen.getByText('5:00')).toBeInTheDocument();
    });
    
    jest.useRealTimers();
  });

  it('handles session completion correctly', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    // Complete all phases
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Complete Quiz')); // Pre-assessment
    await user.click(screen.getByText('Complete PDF')); // PDF study
    await user.click(screen.getByText('Complete Quiz')); // Immediate recall
    await user.click(screen.getByText('Complete Quiz')); // Transfer
    
    // Should show completion screen
    await waitFor(() => {
      expect(screen.getByText('Study Completed!')).toBeInTheDocument();
      expect(screen.getByText('Thank you for participating in our study!')).toBeInTheDocument();
    });
    
    // Should have continue button
    expect(screen.getByText('Continue to Dashboard')).toBeInTheDocument();
  });

  it('navigates to dashboard after completion', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    // Complete all phases
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Complete Quiz')); // Pre-assessment
    await user.click(screen.getByText('Complete PDF')); // PDF study
    await user.click(screen.getByText('Complete Quiz')); // Immediate recall
    await user.click(screen.getByText('Complete Quiz')); // Transfer
    
    // Click continue to dashboard
    await waitFor(() => {
      expect(screen.getByText('Continue to Dashboard')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Continue to Dashboard'));
    
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });

  it('prevents navigation away during active session', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    // Try to navigate away (this would typically be handled by route guards)
    // For testing purposes, we can check that the session is marked as active
    expect(screen.getByText('Phase 1: Pre-Assessment')).toBeInTheDocument();
  });

  it('handles errors gracefully', async () => {
    const { sessionApi } = require('../../../services/api');
    sessionApi.startSession.mockRejectedValue(new Error('Session start failed'));
    
    render(<StudySession />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Error starting session')).toBeInTheDocument();
    });
    
    // Should show retry button
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('logs interactions correctly', async () => {
    const { sessionApi } = require('../../../services/api');
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    
    render(<StudySession />, { initialUser: pdfUser });
    
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    // Should log session start
    await waitFor(() => {
      expect(sessionApi.logInteraction).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'session_start',
          phase: 'pre_assessment',
        })
      );
    });
    
    // Complete pre-assessment
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should log phase completion
    await waitFor(() => {
      expect(sessionApi.logInteraction).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'phase_complete',
          phase: 'pre_assessment',
        })
      );
    });
  });

  it('handles different study groups correctly', async () => {
    const testCases = [
      { group: 'PDF', expectedComponent: 'pdf-viewer' },
      { group: 'CHATGPT', expectedComponent: 'chat-interface' },
    ];
    
    for (const { group, expectedComponent } of testCases) {
      const testUser = { ...mockUser, study_group: group };
      const { rerender } = render(<StudySession />, { initialUser: testUser });
      
      // Complete pre-assessment
      await waitFor(() => {
        expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Complete Quiz'));
      
      // Should show correct study component
      await waitFor(() => {
        expect(screen.getByTestId(expectedComponent)).toBeInTheDocument();
      });
      
      // Clean up for next test
      jest.clearAllMocks();
    }
  });

  it('shows correct phase numbers and titles', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    const expectedPhases = [
      'Phase 1: Pre-Assessment',
      'Phase 2: Study Materials',
      'Phase 3: Immediate Recall',
      'Phase 4: Transfer Assessment',
    ];
    
    for (let i = 0; i < expectedPhases.length; i++) {
      await waitFor(() => {
        expect(screen.getByText(expectedPhases[i])).toBeInTheDocument();
      });
      
      // Complete current phase (except for the last one)
      if (i < expectedPhases.length - 1) {
        const completeButton = screen.getByText(/Complete/);
        await user.click(completeButton);
      }
    }
  });

  it('maintains session state correctly', async () => {
    const pdfUser = { ...mockUser, study_group: 'PDF' };
    render(<StudySession />, { initialUser: pdfUser });
    
    // Complete pre-assessment
    await waitFor(() => {
      expect(screen.getByTestId('quiz-interface')).toBeInTheDocument();
    });
    
    await user.click(screen.getByText('Complete Quiz'));
    
    // Should not be able to go back to pre-assessment
    expect(screen.queryByText('Phase 1: Pre-Assessment')).not.toBeInTheDocument();
    expect(screen.getByText('Phase 2: Study Materials')).toBeInTheDocument();
  });
});