import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import QuizAccessControl from '../components/quiz/QuizAccessControl';
import QuizInterface from '../components/quiz/QuizInterface';
import { QuizAttempt } from '../types';

const QuizPage: React.FC = () => {
  const { quizType } = useParams<{ quizType: string }>();
  const { user } = useAuth();

  if (!quizType || !['pre_assessment', 'immediate_recall', 'transfer'].includes(quizType)) {
    return <Navigate to="/dashboard" replace />;
  }

  const typedQuizType = quizType as 'pre_assessment' | 'immediate_recall' | 'transfer';

  const handleQuizComplete = (attempt: QuizAttempt) => {
    // Handle quiz completion
    console.log('Quiz completed:', attempt);
    
    // Navigate to dashboard after completion
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 2000);
  };

  return (
    <QuizAccessControl quizType={typedQuizType}>
      <QuizInterface
        quizType={typedQuizType}
        sessionId={user?.id || ''}
        onComplete={handleQuizComplete}
      />
    </QuizAccessControl>
  );
};

export default QuizPage;