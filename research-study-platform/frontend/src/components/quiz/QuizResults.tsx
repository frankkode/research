import React, { useState } from 'react';
import { QuizResult, QuizAttempt } from '../../types';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon, 
  TrophyIcon,
  ChartBarIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';

interface QuizResultsProps {
  result: QuizResult;
  onExport?: () => void;
  onReturnToDashboard?: () => void;
}

const QuizResults: React.FC<QuizResultsProps> = ({ 
  result, 
  onExport, 
  onReturnToDashboard 
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'text-green-600';
    if (percentage >= 70) return 'text-blue-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (percentage: number) => {
    if (percentage >= 90) return 'bg-green-50 border-green-200';
    if (percentage >= 70) return 'bg-blue-50 border-blue-200';
    if (percentage >= 50) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getPerformanceLevel = (percentage: number) => {
    if (percentage >= 90) return 'Excellent';
    if (percentage >= 70) return 'Good';
    if (percentage >= 50) return 'Fair';
    return 'Needs Improvement';
  };

  const getCategoryStats = () => {
    const categories: Record<string, { correct: number; total: number }> = {};
    
    result.question_results.forEach(qr => {
      const category = qr.question.category || 'other';
      if (!categories[category]) {
        categories[category] = { correct: 0, total: 0 };
      }
      categories[category].total++;
      if (qr.is_correct) {
        categories[category].correct++;
      }
    });
    
    return Object.entries(categories).map(([category, stats]) => ({
      category: category.replace('_', ' ').toUpperCase(),
      correct: stats.correct,
      total: stats.total,
      percentage: Math.round((stats.correct / stats.total) * 100)
    }));
  };

  const categoryStats = getCategoryStats();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <TrophyIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Quiz Results</h1>
                <p className="text-gray-600">
                  Completed on {new Date(result.attempt.completed_at || '').toLocaleDateString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              {onExport && (
                <button
                  onClick={onExport}
                  className="btn btn-outline flex items-center space-x-2"
                >
                  <DocumentArrowDownIcon className="h-4 w-4" />
                  <span>Export</span>
                </button>
              )}
              
              {onReturnToDashboard && (
                <button
                  onClick={onReturnToDashboard}
                  className="btn btn-primary"
                >
                  Return to Dashboard
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Score Overview */}
        <div className={`rounded-lg border-2 p-8 mb-6 ${getScoreBackground(result.performance.score_percentage)}`}>
          <div className="text-center">
            <div className={`text-6xl font-bold mb-2 ${getScoreColor(result.performance.score_percentage)}`}>
              {result.performance.score_percentage}%
            </div>
            <div className="text-xl font-semibold text-gray-900 mb-2">
              {getPerformanceLevel(result.performance.score_percentage)}
            </div>
            <div className="text-gray-600">
              {result.performance.correct_count} out of {result.performance.total_questions} questions correct
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
              <h3 className="text-lg font-semibold text-gray-900">Accuracy</h3>
            </div>
            <div className="text-3xl font-bold text-green-600 mb-2">
              {result.performance.score_percentage}%
            </div>
            <div className="text-sm text-gray-600">
              {result.performance.correct_count} correct answers
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <ClockIcon className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Time</h3>
            </div>
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {result.performance.time_taken_formatted}
            </div>
            <div className="text-sm text-gray-600">
              Avg: {formatTime(result.performance.average_time_per_question)} per question
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center space-x-3 mb-4">
              <ChartBarIcon className="h-6 w-6 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
            </div>
            <div className="text-3xl font-bold text-purple-600 mb-2">
              {getPerformanceLevel(result.performance.score_percentage)}
            </div>
            <div className="text-sm text-gray-600">
              Based on {result.performance.total_questions} questions
            </div>
          </div>
        </div>

        {/* Category Performance */}
        {categoryStats.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance by Category</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categoryStats.map((category, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900">
                      {category.category}
                    </h4>
                    <span className={`text-sm font-semibold ${getScoreColor(category.percentage)}`}>
                      {category.percentage}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className={`h-2 rounded-full ${
                        category.percentage >= 70 ? 'bg-green-500' : 
                        category.percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${category.percentage}%` }}
                    />
                  </div>
                  <div className="text-xs text-gray-600">
                    {category.correct} / {category.total} correct
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Question Details */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Question Details</h3>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              {showDetails ? 'Hide Details' : 'Show Details'}
            </button>
          </div>
          
          <div className="space-y-4">
            {result.question_results.map((qr, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      qr.is_correct ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {qr.is_correct ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">
                        Question {index + 1}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {qr.question.category?.replace('_', ' ').toUpperCase()} • {qr.question.difficulty?.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className={`text-sm font-medium ${qr.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                      {qr.is_correct ? 'Correct' : 'Incorrect'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatTime(qr.response.time_taken_seconds)}
                    </div>
                  </div>
                </div>
                
                {showDetails && (
                  <div className="mt-4 space-y-3">
                    <div>
                      <p className="text-sm font-medium text-gray-900 mb-2">
                        {qr.question.question_text}
                      </p>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-gray-600 mb-1">Your Answer:</p>
                        <p className={`text-sm ${qr.is_correct ? 'text-green-700' : 'text-red-700'}`}>
                          {qr.question.choices.find(c => c.id === qr.response.selected_choice)?.choice_text || 'No answer'}
                        </p>
                      </div>
                      
                      {!qr.is_correct && (
                        <div>
                          <p className="text-xs text-gray-600 mb-1">Correct Answer:</p>
                          <p className="text-sm text-green-700">
                            {qr.correct_answer.choice_text}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    {qr.question.explanation && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                        <p className="text-xs text-blue-600 font-medium mb-1">Explanation:</p>
                        <p className="text-sm text-blue-800">{qr.question.explanation}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizResults;