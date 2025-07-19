import React, { useState, useEffect } from 'react';
import { Question, QuestionChoice } from '../../types';
import { 
  CheckCircleIcon, 
  ClockIcon, 
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

interface QuestionCardProps {
  question: Question;
  selectedAnswer?: string;
  onAnswerChange: (questionId: string, answerId: string) => void;
  onTimeUpdate: (questionId: string, timeSpent: number) => void;
  isAnswered: boolean;
  questionNumber: number;
  totalQuestions: number;
  timeLimit?: number; // Time limit in seconds for this question
  showResults?: boolean;
  correctAnswerId?: string;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  selectedAnswer,
  onAnswerChange,
  onTimeUpdate,
  isAnswered,
  questionNumber,
  totalQuestions,
  timeLimit,
  showResults = false,
  correctAnswerId
}) => {
  const [startTime] = useState(Date.now());
  const [timeSpent, setTimeSpent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const currentTime = Date.now();
      const elapsed = Math.floor((currentTime - startTime) / 1000);
      setTimeSpent(elapsed);
      onTimeUpdate(question.id, elapsed);
    }, 1000);

    return () => clearInterval(interval);
  }, [question.id, startTime, onTimeUpdate]);

  const handleAnswerSelect = (choiceId: string) => {
    if (!showResults) {
      onAnswerChange(question.id, choiceId);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getChoiceClassName = (choice: QuestionChoice) => {
    const baseClasses = 'w-full text-left p-4 rounded-lg border transition-all duration-200';
    
    if (showResults) {
      if (choice.is_correct) {
        return `${baseClasses} border-green-500 bg-green-50 text-green-800`;
      } else if (choice.id === selectedAnswer && !choice.is_correct) {
        return `${baseClasses} border-red-500 bg-red-50 text-red-800`;
      } else {
        return `${baseClasses} border-gray-300 bg-gray-50 text-gray-600`;
      }
    }
    
    if (choice.id === selectedAnswer) {
      return `${baseClasses} border-blue-500 bg-blue-50 text-blue-800 ring-2 ring-blue-200`;
    }
    
    return `${baseClasses} border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50`;
  };

  const getQuestionTypeIcon = () => {
    switch (question.question_type) {
      case 'multiple_choice':
        return '○';
      case 'true_false':
        return '✓';
      default:
        return '?';
    }
  };

  const getDifficultyColor = () => {
    switch (question.difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const isTimeWarning = timeLimit && timeSpent > timeLimit * 0.8;
  const isTimeUp = Boolean(timeLimit && timeSpent >= timeLimit);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-4xl mx-auto">
      {/* Question Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-gray-400">
              {getQuestionTypeIcon()}
            </span>
            <span className="text-sm font-medium text-gray-600">
              Question {questionNumber} of {totalQuestions}
            </span>
          </div>
          
          {question.difficulty && (
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getDifficultyColor()}`}>
              {question.difficulty}
            </span>
          )}
          
          {question.category && (
            <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800 font-medium">
              {question.category.replace('_', ' ')}
            </span>
          )}
        </div>
        
        {/* Timer */}
        <div className="flex items-center space-x-2">
          <ClockIcon className={`h-5 w-5 ${isTimeWarning ? 'text-red-500' : 'text-gray-500'}`} />
          <span className={`text-sm font-medium ${isTimeWarning ? 'text-red-600' : 'text-gray-600'}`}>
            {formatTime(timeSpent)}
            {timeLimit && (
              <span className="text-gray-400"> / {formatTime(timeLimit)}</span>
            )}
          </span>
        </div>
      </div>

      {/* Time Warning */}
      {isTimeWarning && !isTimeUp && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-4 w-4 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-700">
              Time is running out! Please select your answer soon.
            </span>
          </div>
        </div>
      )}

      {/* Time Up Warning */}
      {isTimeUp && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <ClockIcon className="h-4 w-4 text-red-600 mr-2" />
            <span className="text-sm text-red-700 font-medium">
              Time is up for this question!
            </span>
          </div>
        </div>
      )}

      {/* Question Text */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 leading-relaxed">
          {question.question_text}
        </h3>
        {question.is_required && (
          <span className="text-sm text-red-600 mt-1 block">* Required</span>
        )}
      </div>

      {/* Answer Choices */}
      <div className="space-y-3">
        {question.choices
          .sort((a, b) => a.order - b.order)
          .map((choice, index) => (
            <div key={choice.id} className="relative">
              <label className="cursor-pointer block">
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={choice.id}
                  checked={selectedAnswer === choice.id}
                  onChange={() => handleAnswerSelect(choice.id)}
                  className="sr-only"
                  disabled={showResults || isTimeUp}
                />
                <button
                  type="button"
                  onClick={() => handleAnswerSelect(choice.id)}
                  className={getChoiceClassName(choice)}
                  disabled={showResults || isTimeUp}
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-6 h-6 rounded-full border-2 border-current flex items-center justify-center text-sm font-medium">
                      {String.fromCharCode(65 + index)}
                    </span>
                    <span className="flex-1 text-sm font-medium">
                      {choice.choice_text}
                    </span>
                    {showResults && choice.is_correct && (
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    )}
                  </div>
                </button>
              </label>
            </div>
          ))}
      </div>

      {/* Answer Status */}
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {isAnswered && (
            <div className="flex items-center space-x-2 text-green-600">
              <CheckCircleIcon className="h-4 w-4" />
              <span className="text-sm font-medium">Answered</span>
            </div>
          )}
          {!isAnswered && question.is_required && (
            <span className="text-sm text-gray-500">Please select an answer</span>
          )}
        </div>
        
        {showResults && question.explanation && (
          <div className="text-right">
            <button
              type="button"
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              onClick={() => {
                // Handle explanation toggle if needed
              }}
            >
              View Explanation
            </button>
          </div>
        )}
      </div>

      {/* Explanation (if in results mode) */}
      {showResults && question.explanation && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Explanation:</h4>
          <p className="text-sm text-blue-800">{question.explanation}</p>
        </div>
      )}
    </div>
  );
};

export default QuestionCard;