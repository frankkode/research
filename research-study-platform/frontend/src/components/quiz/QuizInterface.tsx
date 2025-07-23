import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { quizApi } from '../../services/api';
import { Quiz, QuizAttempt, QuizResponse, QuizProgress } from '../../types';
import { getQuizQuestions } from '../../data/quizQuestions';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../common/LoadingSpinner';
import QuestionCard from './QuestionCard';
import QuizCompletionModal from './QuizCompletionModal';
import { 
  ChevronLeftIcon, 
  ChevronRightIcon, 
  CheckCircleIcon, 
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

interface QuizInterfaceProps {
  quizType: 'immediate_recall' | 'transfer' | 'pre_assessment';
  sessionId: string;
  onComplete?: (attempt: QuizAttempt) => void;
}

const QuizInterface: React.FC<QuizInterfaceProps> = ({ 
  quizType, 
  sessionId, 
  onComplete 
}) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, QuizResponse>>({});
  const [questionTimes, setQuestionTimes] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [startTime] = useState(Date.now());
  const [totalTime, setTotalTime] = useState(0);
  const [showReview, setShowReview] = useState(false);
  const [showCompletionModal, setShowCompletionModal] = useState(false);
  const [completedAttempt, setCompletedAttempt] = useState<QuizAttempt | null>(null);
  const [attempt, setAttempt] = useState<QuizAttempt | null>(null);

  // Load quiz data
  useEffect(() => {
    initializeQuiz();
  }, [quizType, sessionId]);

  // Track total time
  useEffect(() => {
    const interval = setInterval(() => {
      setTotalTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const initializeQuiz = async () => {
    try {
      setIsLoading(true);
      
      // Try to load quiz from backend first
      try {
        const response = await quizApi.getQuizByType(quizType);
        const quizData = response.data;
        
        // Transform backend data to frontend format
        const quiz: Quiz = {
          id: `${quizType}-quiz`,
          title: quizData.title || getQuizTitle(quizType),
          description: quizData.description || getQuizDescription(quizType),
          quiz_type: quizType,
          time_limit_minutes: quizData.time_limit_minutes || getTimeLimit(quizType),
          questions: quizData.questions || [],
          can_retake: false,
          max_attempts: 1
        };
        
        setQuiz(quiz);
        
        // Initialize response tracking
        const initialResponses: Record<string, QuizResponse> = {};
        const initialTimes: Record<string, number> = {};
        
        quiz.questions.forEach(question => {
          initialTimes[question.id] = 0;
        });
        
        setResponses(initialResponses);
        setQuestionTimes(initialTimes);
        
      } catch (backendError) {
        console.warn('Failed to load quiz from backend, falling back to hardcoded questions:', backendError);
        
        // Fallback to hardcoded questions
        const questions = getQuizQuestions(quizType);
        const mockQuiz: Quiz = {
          id: `${quizType}-quiz`,
          title: getQuizTitle(quizType),
          description: getQuizDescription(quizType),
          quiz_type: quizType,
          time_limit_minutes: getTimeLimit(quizType),
          questions: questions,
          can_retake: false,
          max_attempts: 1
        };
        
        setQuiz(mockQuiz);
        
        // Initialize response tracking
        const initialResponses: Record<string, QuizResponse> = {};
        const initialTimes: Record<string, number> = {};
        
        questions.forEach(question => {
          initialTimes[question.id] = 0;
        });
        
        setResponses(initialResponses);
        setQuestionTimes(initialTimes);
      }
      
    } catch (error) {
      toast.error('Failed to load quiz');
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const submitQuizToBackend = async (quizAttempt: QuizAttempt, quizType: string) => {
    try {
      // Submit quiz results and update user completion status
      const response = await quizApi.submitQuizResults({
        quiz_type: quizType,
        score: quizAttempt.score || 0,
        total_questions: quizAttempt.total_questions,
        correct_answers: quizAttempt.correct_answers,
        time_taken_seconds: quizAttempt.time_taken_seconds,
        answers: quizAttempt.answers
      });

      // Update user state in localStorage
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response;
    } catch (error) {
      console.error('Failed to submit quiz to backend:', error);
      throw error;
    }
  };

  const getQuizTitle = (type: string) => {
    switch (type) {
      case 'immediate_recall':
        return 'Immediate Recall Assessment';
      case 'transfer':
        return 'Transfer Assessment';
      case 'pre_assessment':
        return 'Pre-Assessment';
      default:
        return 'Quiz';
    }
  };

  const getQuizDescription = (type: string) => {
    switch (type) {
      case 'immediate_recall':
        return 'Test your knowledge of the Linux commands you just studied (10 questions)';
      case 'transfer':
        return 'Apply your Linux knowledge to new scenarios (5 questions)';
      case 'pre_assessment':
        return 'Assess your current knowledge of Linux commands (10 questions)';
      default:
        return 'Quiz assessment';
    }
  };

  const getTimeLimit = (type: string) => {
    switch (type) {
      case 'immediate_recall':
        return 15; // 15 minutes
      case 'transfer':
        return 10; // 10 minutes
      case 'pre_assessment':
        return 15; // 15 minutes
      default:
        return 15;
    }
  };

  const handleAnswerChange = useCallback((questionId: string, answerId: string) => {
    const question = quiz?.questions.find(q => q.id === questionId);
    if (!question) return;

    const selectedChoice = question.choices.find(c => c.id === answerId);
    if (!selectedChoice) return;

    const response: QuizResponse = {
      id: `response-${questionId}-${Date.now()}`,
      question: questionId,
      selected_choice: answerId,
      is_correct: selectedChoice.is_correct,
      time_taken_seconds: questionTimes[questionId] || 0,
      created_at: new Date().toISOString()
    };

    setResponses(prev => ({
      ...prev,
      [questionId]: response
    }));
  }, [quiz, questionTimes]);

  const handleTimeUpdate = useCallback((questionId: string, timeSpent: number) => {
    setQuestionTimes(prev => ({
      ...prev,
      [questionId]: timeSpent
    }));
  }, []);

  const navigateToQuestion = (index: number) => {
    if (index >= 0 && index < (quiz?.questions.length || 0)) {
      setCurrentQuestionIndex(index);
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < (quiz?.questions.length || 0) - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleReview = () => {
    setShowReview(true);
  };

  const handleSubmit = async () => {
    if (!quiz || !user) return;

    // Check if all required questions are answered
    const unansweredRequired = quiz.questions.filter(q => 
      q.is_required && !responses[q.id]
    );

    if (unansweredRequired.length > 0) {
      toast.error(`Please answer all required questions. ${unansweredRequired.length} questions remaining.`);
      return;
    }

    setIsSubmitting(true);

    try {
      // Calculate results
      const correctAnswers = Object.values(responses).filter(r => r.is_correct).length;
      const totalQuestions = quiz.questions.length;
      const scorePercentage = Math.round((correctAnswers / totalQuestions) * 100);

      // Create attempt object
      const quizAttempt: QuizAttempt = {
        id: `attempt-${Date.now()}`,
        quiz: quiz.id,
        user: user.id,
        session: sessionId,
        started_at: new Date(startTime).toISOString(),
        completed_at: new Date().toISOString(),
        is_completed: true,
        score: scorePercentage,
        total_questions: totalQuestions,
        correct_answers: correctAnswers,
        time_taken_seconds: totalTime,
        answers: Object.values(responses)
      };

      // Submit to backend and update user completion status
      await submitQuizToBackend(quizAttempt, quizType);
      
      setAttempt(quizAttempt);
      setCompletedAttempt(quizAttempt);
      setShowCompletionModal(true);
      onComplete?.(quizAttempt);
      
      // Show toast notification
      toast.success('Quiz completed successfully!');
      
    } catch (error) {
      toast.error('Failed to submit quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getProgressPercentage = () => {
    if (!quiz) return 0;
    return Math.round((Object.keys(responses).length / quiz.questions.length) * 100);
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const isCurrentQuestionAnswered = () => {
    const currentQuestion = quiz?.questions[currentQuestionIndex];
    return currentQuestion ? !!responses[currentQuestion.id] : false;
  };

  const getQuestionStatus = (questionIndex: number) => {
    const question = quiz?.questions[questionIndex];
    if (!question) return 'unanswered';
    
    if (responses[question.id]) {
      return 'answered';
    }
    
    if (questionIndex === currentQuestionIndex) {
      return 'current';
    }
    
    return 'unanswered';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Quiz Not Found</h2>
          <p className="text-gray-600 mb-4">The requested quiz could not be loaded.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-primary"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Don't show completion page anymore - use modal instead
  if (attempt && !showCompletionModal) {
    // If we have an attempt but modal is closed, go to dashboard
    navigate('/dashboard');
    return null;
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Quiz Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{quiz.title}</h1>
                <p className="text-gray-600">{quiz.description}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              <div className="text-right">
                <div className="text-sm text-gray-500">Time Elapsed</div>
                <div className="text-lg font-semibold text-gray-900">
                  {formatTime(totalTime)}
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-sm text-gray-500">Progress</div>
                <div className="text-lg font-semibold text-gray-900">
                  {Object.keys(responses).length}/{quiz.questions.length}
                </div>
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Quiz Progress</span>
              <span className="text-sm font-medium text-gray-900">
                {getProgressPercentage()}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>
          </div>
        </div>

        {/* Question Navigation */}
        <div className="bg-white rounded-lg shadow-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">Questions:</span>
              <div className="flex space-x-1">
                {quiz.questions.map((_, index) => {
                  const status = getQuestionStatus(index);
                  return (
                    <button
                      key={index}
                      onClick={() => navigateToQuestion(index)}
                      className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                        status === 'answered'
                          ? 'bg-green-500 text-white'
                          : status === 'current'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                      }`}
                    >
                      {index + 1}
                    </button>
                  );
                })}
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={handleReview}
                className="btn btn-outline text-sm"
              >
                Review Answers
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="btn btn-primary text-sm flex items-center space-x-2"
              >
                {isSubmitting ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <>
                    <CheckCircleIcon className="h-4 w-4" />
                    <span>Submit Quiz</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Question Card */}
        <div className="mb-6">
          <QuestionCard
            question={currentQuestion}
            selectedAnswer={responses[currentQuestion.id]?.selected_choice}
            onAnswerChange={handleAnswerChange}
            onTimeUpdate={handleTimeUpdate}
            isAnswered={isCurrentQuestionAnswered()}
            questionNumber={currentQuestionIndex + 1}
            totalQuestions={quiz.questions.length}
          />
        </div>

        {/* Navigation Controls */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
              className="btn btn-outline flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeftIcon className="h-4 w-4" />
              <span>Previous</span>
            </button>
            
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <span>Question {currentQuestionIndex + 1} of {quiz.questions.length}</span>
              {isCurrentQuestionAnswered() && (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              )}
            </div>
            
            <button
              onClick={handleNext}
              disabled={currentQuestionIndex === quiz.questions.length - 1}
              className="btn btn-outline flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Next</span>
              <ChevronRightIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Quiz Completion Modal */}
      {completedAttempt && (
        <QuizCompletionModal
          attempt={completedAttempt}
          quizType={quizType}
          isOpen={showCompletionModal}
          onClose={() => setShowCompletionModal(false)}
          onContinue={() => {
            setShowCompletionModal(false);
            navigate('/dashboard');
          }}
        />
      )}
    </div>
  );
};

export default QuizInterface;