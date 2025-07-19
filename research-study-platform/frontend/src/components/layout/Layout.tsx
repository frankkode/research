import React, { useState, useEffect } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { ArrowRightOnRectangleIcon, ClockIcon, UserIcon, ChartBarIcon, Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getCompletionBadgeColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-green-100 text-green-800';
    if (percentage >= 75) return 'bg-blue-100 text-blue-800';
    if (percentage >= 50) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo/Title */}
            <div className="flex items-center">
              <h1 className="text-lg sm:text-xl font-semibold text-gray-900">
                <span className="hidden sm:inline">Research Study Platform</span>
                <span className="sm:hidden">Study Platform</span>
              </h1>
            </div>
            
            {user && (
              <>
                {/* Desktop Navigation */}
                <div className="hidden lg:flex items-center space-x-4 xl:space-x-6">
                  {/* Admin Link */}
                  {(user.is_staff || user.is_superuser) && (
                    <Link
                      to="/admin"
                      className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      <ChartBarIcon className="h-4 w-4" />
                      <span>Admin</span>
                    </Link>
                  )}

                  {/* Participant Info */}
                  <div className="flex items-center space-x-2">
                    <UserIcon className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-600">
                      {user.participant_id}
                    </span>
                  </div>

                  {/* Study Group Badge */}
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    user.study_group === 'CHATGPT' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {user.study_group}
                  </span>

                  {/* Completion Progress */}
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    getCompletionBadgeColor(user.completion_percentage)
                  }`}>
                    {user.completion_percentage}% Complete
                  </span>

                  {/* Timer */}
                  <div className="flex items-center space-x-1 text-sm text-gray-600">
                    <ClockIcon className="h-4 w-4" />
                    <span>{formatTime(elapsedTime)}</span>
                  </div>

                  {/* Logout Button */}
                  <button
                    onClick={logout}
                    className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                  >
                    <ArrowRightOnRectangleIcon className="h-4 w-4" />
                    <span>Logout</span>
                  </button>
                </div>

                {/* Mobile Navigation */}
                <div className="lg:hidden flex items-center space-x-2">
                  {/* Essential mobile info */}
                  <div className="flex items-center space-x-1 text-sm text-gray-600">
                    <ClockIcon className="h-4 w-4" />
                    <span>{formatTime(elapsedTime)}</span>
                  </div>
                  
                  {/* Progress indicator */}
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    getCompletionBadgeColor(user.completion_percentage)
                  }`}>
                    {user.completion_percentage}%
                  </span>

                  {/* Mobile menu button */}
                  <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                  >
                    {isMobileMenuOpen ? (
                      <XMarkIcon className="h-5 w-5" />
                    ) : (
                      <Bars3Icon className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {user && isMobileMenuOpen && (
          <div className="lg:hidden border-t bg-white">
            <div className="px-4 py-3 space-y-3">
              {/* Admin Link */}
              {(user.is_staff || user.is_superuser) && (
                <Link
                  to="/admin"
                  className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <ChartBarIcon className="h-4 w-4" />
                  <span>Admin Dashboard</span>
                </Link>
              )}

              {/* User Info */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <UserIcon className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-600">
                    Participant: {user.participant_id}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    user.study_group === 'CHATGPT' 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    Study Group: {user.study_group}
                  </span>
                </div>
              </div>

              {/* Logout */}
              <button
                onClick={() => {
                  logout();
                  setIsMobileMenuOpen(false);
                }}
                className="flex items-center space-x-2 text-sm text-red-600 hover:text-red-800 transition-colors w-full"
              >
                <ArrowRightOnRectangleIcon className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Navigation/Progress Bar */}
      {user && (
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-3 sm:py-0 sm:h-12">
              {/* Mobile Progress Steps - Horizontal scroll */}
              <div className="flex items-center space-x-4 sm:space-x-8 overflow-x-auto pb-2 sm:pb-0">
                <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
                  <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${
                    user.consent_completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                  <span className={`text-xs sm:text-sm whitespace-nowrap ${
                    user.consent_completed ? 'text-green-700' : 'text-gray-500'
                  }`}>Consent</span>
                </div>
                
                <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
                  <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${
                    user.pre_quiz_completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                  <span className={`text-xs sm:text-sm whitespace-nowrap ${
                    user.pre_quiz_completed ? 'text-green-700' : 'text-gray-500'
                  }`}>Pre-Quiz</span>
                </div>
                
                <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
                  <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${
                    user.interaction_completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                  <span className={`text-xs sm:text-sm whitespace-nowrap ${
                    user.interaction_completed ? 'text-green-700' : 'text-gray-500'
                  }`}>Learning</span>
                </div>
                
                <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
                  <div className={`w-2 h-2 sm:w-3 sm:h-3 rounded-full ${
                    user.post_quiz_completed ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                  <span className={`text-xs sm:text-sm whitespace-nowrap ${
                    user.post_quiz_completed ? 'text-green-700' : 'text-gray-500'
                  }`}>Post-Quiz</span>
                </div>
              </div>
              
              <div className="text-xs sm:text-sm text-gray-600 mt-2 sm:mt-0 text-center sm:text-right">
                <span className="sm:hidden">Progress: </span>
                <span className="hidden sm:inline">Study Progress: </span>
                {user.completion_percentage}%
              </div>
            </div>
          </div>
        </nav>
      )}
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;