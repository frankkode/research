import React from 'react';
import { CheckCircleIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { QuizAttempt } from '../../types';

interface QuizCompletionModalProps {
  attempt: QuizAttempt;
  quizType: string;
  isOpen: boolean;
  onClose: () => void;
  onContinue: () => void;
}

const QuizCompletionModal: React.FC<QuizCompletionModalProps> = ({
  attempt,
  quizType,
  isOpen,
  onClose,
  onContinue
}) => {
  if (!isOpen) return null;

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getPerformanceLevel = (percentage: number) => {
    if (percentage >= 90) return { level: 'Excellent', color: 'text-green-600', bgColor: 'bg-green-50' };
    if (percentage >= 70) return { level: 'Good', color: 'text-blue-600', bgColor: 'bg-blue-50' };
    if (percentage >= 50) return { level: 'Fair', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { level: 'Needs Improvement', color: 'text-red-600', bgColor: 'bg-red-50' };
  };

  const isPostQuiz = quizType === 'immediate_recall';
  const performance = getPerformanceLevel(attempt.score || 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 ${isPostQuiz ? 'bg-gradient-to-r from-green-400 to-blue-500' : 'bg-green-100'} rounded-full flex items-center justify-center`}>
              <CheckCircleIcon className={`h-6 w-6 ${isPostQuiz ? 'text-white' : 'text-green-600'}`} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {isPostQuiz ? '🎉 Congratulations!' : 'Quiz Completed!'}
              </h2>
              <p className="text-gray-600">
                {isPostQuiz ? 'Post-assessment completed successfully!' : 'Assessment completed successfully!'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Score Display */}
          <div className={`${performance.bgColor} border border-gray-200 rounded-lg p-6 mb-6`}>
            <div className="text-center">
              <div className={`text-5xl font-bold mb-2 ${performance.color}`}>
                {attempt.score}%
              </div>
              <div className="text-lg font-semibold text-gray-900 mb-2">
                {performance.level}
              </div>
              <div className="text-gray-600">
                {attempt.correct_answers} out of {attempt.total_questions} questions correct
              </div>
            </div>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-blue-600">
                {attempt.score}%
              </div>
              <div className="text-sm text-blue-800">Score</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-green-600">
                {attempt.correct_answers}/{attempt.total_questions}
              </div>
              <div className="text-sm text-green-800">Correct</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg text-center">
              <div className="text-2xl font-bold text-gray-600">
                {formatTime(attempt.time_taken_seconds)}
              </div>
              <div className="text-sm text-gray-800">Time</div>
            </div>
          </div>

          {/* Post-Quiz Special Message */}
          {isPostQuiz && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="text-xl font-semibold text-blue-900 mb-3">
                📚 What's Next?
              </h3>
              <div className="space-y-3 text-blue-800">
                <p className="flex items-start space-x-2">
                  <span className="text-blue-500">⏰</span>
                  <span><strong>Transfer Knowledge Quiz:</strong> You'll be able to access the final transfer quiz in <strong>24 hours</strong></span>
                </p>
                <p className="flex items-start space-x-2">
                  <span className="text-blue-500">📧</span>
                  <span><strong>Automated Reminder:</strong> We'll send you a link via email when it's available</span>
                </p>
                <p className="flex items-start space-x-2">
                  <span className="text-blue-500">💬</span>
                  <span><strong>Need Help?:</strong> If you don't receive the link within 24 hours, please contact the admin</span>
                </p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Close
            </button>
            <button
              onClick={onContinue}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Continue to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizCompletionModal;