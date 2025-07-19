import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  LockClosedIcon, 
  ClockIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon 
} from '@heroicons/react/24/outline';

interface QuizAccessControlProps {
  quizType: 'immediate_recall' | 'transfer' | 'pre_assessment';
  children: React.ReactNode;
}

const QuizAccessControl: React.FC<QuizAccessControlProps> = ({ quizType, children }) => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const canAccess = () => {
    if (!user) return false;
    
    switch (quizType) {
      case 'pre_assessment':
        return user.consent_completed && !user.pre_quiz_completed;
      case 'immediate_recall':
        return user.consent_completed && 
               user.pre_quiz_completed && 
               user.interaction_completed && 
               !user.post_quiz_completed;
      case 'transfer':
        // Transfer quiz available 24 hours after immediate recall
        if (!user.post_quiz_completed || user.study_completed) {
          return false;
        }
        
        // Check if 24 hours have passed since post_quiz_completed_at
        if (user.post_quiz_completed_at) {
          const postQuizTime = new Date(user.post_quiz_completed_at);
          const now = new Date();
          const hoursDiff = (now.getTime() - postQuizTime.getTime()) / (1000 * 60 * 60);
          return hoursDiff >= 24;
        }
        
        return false;
      default:
        return false;
    }
  };

  const getAccessMessage = () => {
    if (!user) return 'Please log in to access this quiz.';
    
    switch (quizType) {
      case 'pre_assessment':
        if (!user.consent_completed) {
          return 'Please complete the consent form before taking the pre-assessment.';
        }
        if (user.pre_quiz_completed) {
          return 'You have already completed the pre-assessment quiz.';
        }
        break;
        
      case 'immediate_recall':
        if (!user.consent_completed) {
          return 'Please complete the consent form first.';
        }
        if (!user.pre_quiz_completed) {
          return 'Please complete the pre-assessment quiz first.';
        }
        if (!user.interaction_completed) {
          return 'Please complete your learning session before taking this quiz.';
        }
        if (user.post_quiz_completed) {
          return 'You have already completed the immediate recall quiz.';
        }
        break;
        
      case 'transfer':
        if (!user.post_quiz_completed) {
          return 'Please complete the immediate recall quiz first.';
        }
        if (user.study_completed) {
          return 'You have already completed the transfer quiz.';
        }
        
        // Check if 24 hours have passed since post_quiz completion
        if (user.post_quiz_completed_at) {
          const postQuizTime = new Date(user.post_quiz_completed_at);
          const now = new Date();
          const hoursDiff = (now.getTime() - postQuizTime.getTime()) / (1000 * 60 * 60);
          
          if (hoursDiff < 24) {
            const hoursRemaining = Math.ceil(24 - hoursDiff);
            return `The transfer quiz will be available in ${hoursRemaining} hours. Please wait 24 hours after completing the immediate recall quiz.`;
          }
        } else {
          return 'The transfer quiz will be available 24 hours after completing the immediate recall quiz.';
        }
        
        return '';
        
      default:
        return 'Quiz access not available.';
    }
    
    return '';
  };

  const getQuizTitle = () => {
    switch (quizType) {
      case 'pre_assessment':
        return 'Pre-Assessment Quiz';
      case 'immediate_recall':
        return 'Immediate Recall Quiz';
      case 'transfer':
        return 'Transfer Quiz';
      default:
        return 'Quiz';
    }
  };

  const getQuizDescription = () => {
    switch (quizType) {
      case 'pre_assessment':
        return 'Assess your current knowledge of Linux commands before the study.';
      case 'immediate_recall':
        return 'Test your recall of the Linux commands you just studied.';
      case 'transfer':
        return 'Apply your Linux knowledge to new scenarios and problems.';
      default:
        return 'Quiz assessment';
    }
  };

  const getRequiredSteps = () => {
    switch (quizType) {
      case 'pre_assessment':
        return [
          { step: 'Consent Form', completed: user?.consent_completed || false }
        ];
      case 'immediate_recall':
        return [
          { step: 'Consent Form', completed: user?.consent_completed || false },
          { step: 'Pre-Assessment', completed: user?.pre_quiz_completed || false },
          { step: 'Learning Session', completed: user?.interaction_completed || false }
        ];
      case 'transfer':
        return [
          { step: 'Consent Form', completed: user?.consent_completed || false },
          { step: 'Pre-Assessment', completed: user?.pre_quiz_completed || false },
          { step: 'Learning Session', completed: user?.interaction_completed || false },
          { step: 'Immediate Recall Quiz', completed: user?.post_quiz_completed || false }
        ];
      default:
        return [];
    }
  };

  if (canAccess()) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <LockClosedIcon className="h-8 w-8 text-red-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {getQuizTitle()} - Access Restricted
            </h2>
            <p className="text-gray-600 mb-4">
              {getQuizDescription()}
            </p>
          </div>
          
          <div className="mb-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
                <div>
                  <p className="text-sm font-medium text-red-800">Access Denied</p>
                  <p className="text-sm text-red-700 mt-1">
                    {getAccessMessage()}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Required Steps to Access This Quiz
            </h3>
            <div className="space-y-3">
              {getRequiredSteps().map((requirement, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                    requirement.completed ? 'bg-green-100' : 'bg-gray-100'
                  }`}>
                    {requirement.completed ? (
                      <CheckCircleIcon className="h-4 w-4 text-green-600" />
                    ) : (
                      <div className="w-2 h-2 bg-gray-400 rounded-full" />
                    )}
                  </div>
                  <span className={`text-sm ${
                    requirement.completed ? 'text-green-700' : 'text-gray-600'
                  }`}>
                    {requirement.step}
                  </span>
                  {requirement.completed && (
                    <span className="text-xs text-green-600 font-medium">
                      ✓ Completed
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          {quizType === 'transfer' && (
            <div className="mb-8">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <ClockIcon className="h-5 w-5 text-blue-600 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-blue-800">
                      24-Hour Waiting Period
                    </p>
                    <p className="text-sm text-blue-700 mt-1">
                      The transfer quiz becomes available 24 hours after completing the immediate recall quiz to test knowledge retention.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="text-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="btn btn-primary"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizAccessControl;