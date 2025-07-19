import React from 'react';
import { screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { render, mockUser, mockQuiz, mockQuizQuestion } from '../../../test-utils';
import QuizInterface from '../QuizInterface';
import { toast } from 'react-hot-toast';

// Mock the quiz questions data
jest.mock('../../../data/quizQuestions', () => ({
  getQuizQuestions: jest.fn((quizType) => [
    {
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
    },
    {
      id: 'q2',
      question_text: 'What command changes directory?',
      question_type: 'multiple_choice',
      is_required: true,
      points: 10,
      choices: [
        { id: 'b1', text: 'cd', is_correct: true },
        { id: 'b2', text: 'dir', is_correct: false },
        { id: 'b3', text: 'change', is_correct: false },
        { id: 'b4', text: 'goto', is_correct: false },
      ],
    },
  ]),
}));

// Mock the QuestionCard component
jest.mock('../QuestionCard', () => {
  return function MockQuestionCard({ question, onAnswerChange, onTimeUpdate, questionNumber }: any) {
    return (
      <div data-testid="question-card">
        <h3>Question {questionNumber}: {question.question_text}</h3>
        <div>
          {question.choices.map((choice: any) => (
            <button
              key={choice.id}
              data-testid={`choice-${choice.id}`}
              onClick={() => onAnswerChange(question.id, choice.id)}
            >
              {choice.text}
            </button>
          ))}
        </div>
        <button onClick={() => onTimeUpdate(question.id, 30)}>
          Update Time
        </button>
      </div>
    );
  };
});

// Mock the API
jest.mock('../../../services/api', () => ({
  quizApi: {
    submitQuiz: jest.fn().mockResolvedValue({ success: true }),
  },
}));

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('QuizInterface', () => {
  const user = userEvent.setup();
  const mockOnComplete = jest.fn();

  const defaultProps = {
    quizType: 'pre_assessment' as const,
    sessionId: 'test-session-123',
    onComplete: mockOnComplete,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  it('renders loading state initially', () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('renders quiz interface after loading', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    expect(screen.getByText('Assess your current knowledge of Linux commands (10 questions)')).toBeInTheDocument();
    expect(screen.getByTestId('question-card')).toBeInTheDocument();
  });

  it('displays correct quiz titles for different types', async () => {
    const { rerender } = render(
      <QuizInterface {...defaultProps} quizType="immediate_recall" />,
      { initialUser: mockUser }
    );
    
    await waitFor(() => {
      expect(screen.getByText('Immediate Recall Assessment')).toBeInTheDocument();
    });

    rerender(
      <QuizInterface {...defaultProps} quizType="transfer" />,
      { initialUser: mockUser }
    );
    
    await waitFor(() => {
      expect(screen.getByText('Transfer Assessment')).toBeInTheDocument();
    });
  });

  it('shows progress information correctly', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    expect(screen.getByText('0/2')).toBeInTheDocument(); // Progress: 0 out of 2 questions
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument();
  });

  it('tracks elapsed time correctly', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Initially shows 0:00
    expect(screen.getByText('0:00')).toBeInTheDocument();

    // Advance time by 30 seconds
    act(() => {
      jest.advanceTimersByTime(30000);
    });

    await waitFor(() => {
      expect(screen.getByText('0:30')).toBeInTheDocument();
    });
  });

  it('handles answer selection correctly', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Select an answer
    await user.click(screen.getByTestId('choice-a1'));

    // Progress should update
    await waitFor(() => {
      expect(screen.getByText('1/2')).toBeInTheDocument();
    });
  });

  it('navigates between questions correctly', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Should show first question
    expect(screen.getByText('Question 1: What command lists files in Linux?')).toBeInTheDocument();

    // Click Next button
    await user.click(screen.getByText('Next'));

    // Should show second question
    expect(screen.getByText('Question 2: What command changes directory?')).toBeInTheDocument();

    // Click Previous button
    await user.click(screen.getByText('Previous'));

    // Should show first question again
    expect(screen.getByText('Question 1: What command lists files in Linux?')).toBeInTheDocument();
  });

  it('disables navigation buttons appropriately', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Previous button should be disabled on first question
    const prevButton = screen.getByText('Previous');
    expect(prevButton).toBeDisabled();

    // Go to last question
    await user.click(screen.getByText('Next'));

    // Next button should be disabled on last question
    const nextButton = screen.getByText('Next');
    expect(nextButton).toBeDisabled();

    // Previous button should be enabled
    expect(prevButton).not.toBeDisabled();
  });

  it('allows direct question navigation via number buttons', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Click on question 2 directly
    await user.click(screen.getByText('2'));

    // Should show second question
    expect(screen.getByText('Question 2: What command changes directory?')).toBeInTheDocument();
  });

  it('shows question status correctly in navigation', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Question 1 should be current (blue)
    const q1Button = screen.getByText('1');
    expect(q1Button).toHaveClass('bg-blue-500');

    // Answer question 1
    await user.click(screen.getByTestId('choice-a1'));

    // Question 1 should now be answered (green)
    await waitFor(() => {
      expect(q1Button).toHaveClass('bg-green-500');
    });
  });

  it('prevents submission with unanswered required questions', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Try to submit without answering questions
    await user.click(screen.getByText('Submit Quiz'));

    // Should show error toast
    expect(toast.error).toHaveBeenCalledWith(
      expect.stringContaining('Please answer all required questions')
    );
  });

  it('submits quiz successfully when all questions are answered', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Answer first question
    await user.click(screen.getByTestId('choice-a1'));

    // Navigate to second question and answer it
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByTestId('choice-b1'));

    // Submit quiz
    await user.click(screen.getByText('Submit Quiz'));

    // Should show success message and completion screen
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Quiz completed successfully!');
    });

    // Should call onComplete callback
    expect(mockOnComplete).toHaveBeenCalledWith(
      expect.objectContaining({
        score: 100, // Both answers correct
        correct_answers: 2,
        total_questions: 2,
      })
    );
  });

  it('displays completion screen after successful submission', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Answer both questions
    await user.click(screen.getByTestId('choice-a1'));
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByTestId('choice-b1'));

    // Submit quiz
    await user.click(screen.getByText('Submit Quiz'));

    // Should show completion screen
    await waitFor(() => {
      expect(screen.getByText('Quiz Completed!')).toBeInTheDocument();
    });

    expect(screen.getByText('100%')).toBeInTheDocument(); // Score
    expect(screen.getByText('2/2')).toBeInTheDocument(); // Correct answers
    expect(screen.getByText('Continue to Dashboard')).toBeInTheDocument();
  });

  it('calculates score correctly with wrong answers', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Answer first question correctly, second incorrectly
    await user.click(screen.getByTestId('choice-a1'));
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByTestId('choice-b2')); // Wrong answer

    // Submit quiz
    await user.click(screen.getByText('Submit Quiz'));

    await waitFor(() => {
      expect(screen.getByText('Quiz Completed!')).toBeInTheDocument();
    });

    expect(screen.getByText('50%')).toBeInTheDocument(); // 1/2 correct = 50%
    expect(screen.getByText('1/2')).toBeInTheDocument(); // 1 correct out of 2
  });

  it('handles time tracking for questions', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Simulate time update
    await user.click(screen.getByText('Update Time'));

    // Answer and submit
    await user.click(screen.getByTestId('choice-a1'));
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByTestId('choice-b1'));
    await user.click(screen.getByText('Submit Quiz'));

    // Should call onComplete with time tracking
    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledWith(
        expect.objectContaining({
          time_taken_seconds: expect.any(Number),
        })
      );
    });
  });

  it('handles review answers functionality', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Review button should be present
    expect(screen.getByText('Review Answers')).toBeInTheDocument();

    // Click review button
    await user.click(screen.getByText('Review Answers'));

    // Should trigger review mode (implementation depends on actual review functionality)
  });

  it('redirects to dashboard when quiz cannot be loaded', async () => {
    // Mock the quiz questions to return empty array
    const { getQuizQuestions } = require('../../../data/quizQuestions');
    getQuizQuestions.mockReturnValue([]);

    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to load quiz');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows loading spinner while submitting', async () => {
    render(<QuizInterface {...defaultProps} />, { initialUser: mockUser });
    
    await waitFor(() => {
      expect(screen.getByText('Pre-Assessment')).toBeInTheDocument();
    });

    // Answer questions
    await user.click(screen.getByTestId('choice-a1'));
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByTestId('choice-b1'));

    // Click submit
    await user.click(screen.getByText('Submit Quiz'));

    // Should show loading spinner briefly
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('handles different quiz types with correct time limits', async () => {
    const { rerender } = render(
      <QuizInterface {...defaultProps} quizType="immediate_recall" />,
      { initialUser: mockUser }
    );
    
    await waitFor(() => {
      expect(screen.getByText('Test your knowledge of the Linux commands you just studied (10 questions)')).toBeInTheDocument();
    });

    rerender(
      <QuizInterface {...defaultProps} quizType="transfer" />,
      { initialUser: mockUser }
    );
    
    await waitFor(() => {
      expect(screen.getByText('Apply your Linux knowledge to new scenarios (5 questions)')).toBeInTheDocument();
    });
  });
});