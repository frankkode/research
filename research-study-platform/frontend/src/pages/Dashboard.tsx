import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { studyApi } from '../services/api';
import { Study, StudySession } from '../types';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { 
  AcademicCapIcon, 
  BookOpenIcon, 
  ChatBubbleLeftRightIcon, 
  CheckCircleIcon,
  ClockIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [studies, setStudies] = useState<Study[]>([]);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [forceRefresh, setForceRefresh] = useState(0);

  // Debug user completion status
  useEffect(() => {
    if (user) {
      console.log('Dashboard user data updated:', {
        consent_completed: user.consent_completed,
        pre_quiz_completed: user.pre_quiz_completed,
        interaction_completed: user.interaction_completed,
        post_quiz_completed: user.post_quiz_completed,
        study_group: user.study_group,
        post_quiz_button_should_show: user.consent_completed && user.interaction_completed
      });
    }
  }, [user]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Dashboard: Fetching data...');
        // Force refresh user data multiple times to ensure we get the latest state
        await refreshUser();
        console.log('Dashboard: First user data refresh completed');
        
        // Wait a moment and refresh again
        await new Promise(resolve => setTimeout(resolve, 500));
        await refreshUser();
        console.log('Dashboard: Second user data refresh completed');
        
        const [studiesResponse, sessionsResponse] = await Promise.all([
          studyApi.getActiveStudies(),
          studyApi.getMySessions()
        ]);
        
        setStudies(studiesResponse.data);
        setSessions(sessionsResponse.data);
        console.log('Dashboard: Data loaded successfully');
      } catch (error) {
        console.error('Dashboard: Failed to load data:', error);
        toast.error('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [refreshUser, forceRefresh]); // Include forceRefresh to allow manual refresh

  const handleJoinStudy = async (studyId: string) => {
    try {
      const response = await studyApi.joinStudy(studyId);
      toast.success('Successfully joined study!');
      navigate(`/study/${response.data.session_id}`);
    } catch (error) {
      toast.error('Failed to join study');
    }
  };

  const handleContinueSession = (sessionId: string) => {
    navigate(`/study/${sessionId}`);
  };

  const getNextStepMessage = () => {
    if (!user) return '';
    
    if (!user.consent_completed) {
      return 'Please complete the consent form to begin';
    }
    if (!user.pre_quiz_completed) {
      return 'Take the pre-assessment quiz';
    }
    if (!user.interaction_completed) {
      return user.study_group === 'CHATGPT' 
        ? 'Complete the ChatGPT learning session'
        : 'Complete the PDF learning session';
    }
    if (!user.post_quiz_completed) {
      return 'Take the post-assessment quiz';
    }
    return 'Study completed - thank you for participating!';
  };

  const handleStartLearningSession = async () => {
    if (!user) return;
    
    try {
      // Create or get current study session
      const session = await studyApi.createOrGetSession({
        user_agent: navigator.userAgent
      });
      
      // Navigate to study session
      navigate(`/study/${session.data.session_id}`);
    } catch (error) {
      console.error('Failed to start learning session:', error);
      toast.error('Failed to start learning session');
    }
  };

  const getStepIcon = (step: string) => {
    switch(step) {
      case 'consent':
        return <DocumentTextIcon className="h-5 w-5" />;
      case 'pre_quiz':
        return <AcademicCapIcon className="h-5 w-5" />;
      case 'interaction':
        return user?.study_group === 'CHATGPT' 
          ? <ChatBubbleLeftRightIcon className="h-5 w-5" />
          : <BookOpenIcon className="h-5 w-5" />;
      case 'post_quiz':
        return <AcademicCapIcon className="h-5 w-5" />;
      default:
        return <CheckCircleIcon className="h-5 w-5" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-white shadow rounded-lg p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
              Welcome, {user?.username}!
            </h1>
            <p className="text-gray-600 mt-1">
              Linux Learning Study - {user?.study_group} Group
            </p>
          </div>
          <div className="text-left sm:text-right">
            <p className="text-sm text-gray-500">Participant ID</p>
            <p className="text-lg font-semibold text-gray-900">{user?.participant_id}</p>
            <button
              onClick={() => setForceRefresh(prev => prev + 1)}
              className="mt-2 text-xs text-blue-600 hover:text-blue-800"
            >
              Refresh Status
            </button>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-primary-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                user?.study_group === 'CHATGPT' ? 'bg-blue-500' : 'bg-green-500'
              }`} />
              <h3 className="font-semibold text-gray-800">Study Group</h3>
            </div>
            <p className="text-xl font-bold text-gray-700 mt-1">
              {user?.study_group}
            </p>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <ClockIcon className="h-4 w-4 text-blue-600" />
              <h3 className="font-semibold text-blue-800">Progress</h3>
            </div>
            <p className="text-xl font-bold text-blue-600 mt-1">
              {user?.completion_percentage}%
            </p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-4 w-4 text-green-600" />
              <h3 className="font-semibold text-green-800">Completed</h3>
            </div>
            <p className="text-xl font-bold text-green-600 mt-1">
              {[user?.consent_completed, user?.pre_quiz_completed, user?.interaction_completed, user?.post_quiz_completed].filter(Boolean).length}/4
            </p>
          </div>
          
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <AcademicCapIcon className="h-4 w-4 text-yellow-600" />
              <h3 className="font-semibold text-yellow-800">Status</h3>
            </div>
            <p className="text-sm font-medium text-yellow-700 mt-1">
              {user?.study_completed ? 'Complete' : 'Active'}
            </p>
          </div>
        </div>

        {/* Next Step */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Next Step</h3>
          <p className="text-gray-600">{getNextStepMessage()}</p>
        </div>
      </div>

      {/* Study Steps */}
      <div className="bg-white shadow rounded-lg p-4 sm:p-6">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 mb-6">Study Progress</h2>
        
        <div className="space-y-4">
          {/* Consent */}
          <div className={`flex flex-col sm:flex-row sm:items-center p-4 rounded-lg border space-y-3 sm:space-y-0 ${
            user?.consent_completed 
              ? 'border-green-200 bg-green-50' 
              : 'border-gray-200 bg-gray-50'
          }`}>
            <div className="flex items-center flex-1">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-4 ${
                user?.consent_completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {getStepIcon('consent')}
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Informed Consent</h3>
                <p className="text-sm text-gray-600">Review and agree to participate in the study</p>
              </div>
            </div>
            {user?.consent_completed ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
            ) : (
              <button
                onClick={() => navigate('/consent')}
                className="btn btn-primary text-sm w-full sm:w-auto"
              >
                Start Consent
              </button>
            )}
          </div>

          {/* Pre-Quiz */}
          <div className={`flex flex-col sm:flex-row sm:items-center p-4 rounded-lg border space-y-3 sm:space-y-0 ${
            user?.pre_quiz_completed 
              ? 'border-green-200 bg-green-50' 
              : 'border-gray-200 bg-gray-50'
          }`}>
            <div className="flex items-center flex-1">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-4 ${
                user?.pre_quiz_completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {getStepIcon('pre_quiz')}
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Pre-Assessment Quiz</h3>
                <p className="text-sm text-gray-600">Test your current Linux knowledge</p>
              </div>
            </div>
            {user?.pre_quiz_completed ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
            ) : (
              user?.consent_completed && (
                <button
                  onClick={() => navigate('/quiz/pre_assessment')}
                  className="btn btn-primary text-sm w-full sm:w-auto"
                >
                  Start Quiz
                </button>
              )
            )}
          </div>

          {/* Learning Session */}
          <div className={`flex flex-col sm:flex-row sm:items-center p-4 rounded-lg border space-y-3 sm:space-y-0 ${
            user?.interaction_completed 
              ? 'border-green-200 bg-green-50' 
              : 'border-gray-200 bg-gray-50'
          }`}>
            <div className="flex items-center flex-1">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-4 ${
                user?.interaction_completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {getStepIcon('interaction')}
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">
                  {user?.study_group === 'CHATGPT' ? 'ChatGPT Learning Session' : 'PDF Learning Session'}
                </h3>
                <p className="text-sm text-gray-600">
                  {user?.study_group === 'CHATGPT' 
                    ? 'Learn Linux commands through interactive chat' 
                    : 'Study Linux commands from the provided document'}
                </p>
              </div>
            </div>
            {(() => {
              console.log('Learning session render check:', {
                interaction_completed: user?.interaction_completed,
                consent_completed: user?.consent_completed,
                pre_quiz_completed: user?.pre_quiz_completed,
                userId: user?.id,
                participantId: user?.participant_id
              });
              
              if (user?.interaction_completed) {
                return <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />;
              }
              
              if (user?.consent_completed && user?.pre_quiz_completed) {
                return (
                  <button
                    onClick={handleStartLearningSession}
                    className="btn btn-primary text-sm w-full sm:w-auto"
                  >
                    Start Session
                  </button>
                );
              }
              
              return (
                <span className="text-sm text-gray-500 text-center sm:text-right">
                  Complete previous steps first
                </span>
              );
            })()}
          </div>

          {/* Post-Quiz */}
          <div className={`flex flex-col sm:flex-row sm:items-center p-4 rounded-lg border space-y-3 sm:space-y-0 ${
            user?.post_quiz_completed 
              ? 'border-green-200 bg-green-50' 
              : 'border-gray-200 bg-gray-50'
          }`}>
            <div className="flex items-center flex-1">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-4 ${
                user?.post_quiz_completed 
                  ? 'bg-green-500 text-white' 
                  : 'bg-gray-300 text-gray-600'
              }`}>
                {getStepIcon('post_quiz')}
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Post-Assessment Quiz</h3>
                <p className="text-sm text-gray-600">Test your Linux knowledge after learning</p>
              </div>
            </div>
            {user?.post_quiz_completed ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500 flex-shrink-0" />
            ) : (
              (() => {
                const canStartPostQuiz = user?.consent_completed && 
                                        user?.pre_quiz_completed && 
                                        user?.interaction_completed && 
                                        !user?.post_quiz_completed;
                console.log('Post-quiz button render check:', {
                  consent_completed: user?.consent_completed,
                  pre_quiz_completed: user?.pre_quiz_completed,
                  interaction_completed: user?.interaction_completed,
                  post_quiz_completed: user?.post_quiz_completed,
                  canStartPostQuiz,
                  userId: user?.id,
                  participantId: user?.participant_id,
                  timestamp: new Date().toISOString()
                });
                
                if (canStartPostQuiz) {
                  return (
                    <button
                      onClick={() => navigate('/quiz/immediate_recall')}
                      className="btn btn-primary text-sm w-full sm:w-auto"
                    >
                      Start Quiz
                    </button>
                  );
                }
                
                // Show more specific message based on what's missing
                if (!user?.consent_completed) {
                  return (
                    <span className="text-sm text-gray-500 text-center sm:text-right">
                      Complete consent form first
                    </span>
                  );
                }
                
                if (!user?.pre_quiz_completed) {
                  return (
                    <span className="text-sm text-gray-500 text-center sm:text-right">
                      Complete pre-assessment quiz first
                    </span>
                  );
                }
                
                if (!user?.interaction_completed) {
                  return (
                    <span className="text-sm text-gray-500 text-center sm:text-right">
                      Complete learning session first
                    </span>
                  );
                }
                
                return (
                  <span className="text-sm text-gray-500 text-center sm:text-right">
                    Complete previous steps first
                  </span>
                );
              })()
            )}
          </div>
        </div>
      </div>

      {/* Transfer Quiz (if applicable) */}
      {user?.post_quiz_completed && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">24-Hour Follow-up</h2>
          
          <div className={`flex items-center p-4 rounded-lg border ${
            user?.study_completed 
              ? 'border-green-200 bg-green-50' 
              : 'border-blue-200 bg-blue-50'
          }`}>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full mr-4 ${
              user?.study_completed 
                ? 'bg-green-500 text-white' 
                : 'bg-blue-500 text-white'
            }`}>
              <AcademicCapIcon className="h-5 w-5" />
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900">Transfer Assessment</h3>
              <p className="text-sm text-gray-600">
                Apply your Linux knowledge to new scenarios (available 24 hours after immediate recall)
              </p>
            </div>
            {user?.study_completed ? (
              <CheckCircleIcon className="h-5 w-5 text-green-500" />
            ) : (
              (() => {
                // Check if 24 hours have passed since post_quiz completion
                if (user.post_quiz_completed_at) {
                  const postQuizTime = new Date(user.post_quiz_completed_at);
                  const now = new Date();
                  const hoursDiff = (now.getTime() - postQuizTime.getTime()) / (1000 * 60 * 60);
                  
                  if (hoursDiff >= 24) {
                    return (
                      <button
                        onClick={() => navigate('/quiz/transfer')}
                        className="btn btn-primary text-sm"
                      >
                        Start Transfer Quiz
                      </button>
                    );
                  } else {
                    const hoursRemaining = Math.ceil(24 - hoursDiff);
                    return (
                      <div className="text-right">
                        <span className="text-sm text-gray-500">
                          Available in {hoursRemaining} hours
                        </span>
                        <div className="mt-1">
                          <ClockIcon className="h-4 w-4 text-gray-400" />
                        </div>
                      </div>
                    );
                  }
                } else {
                  return (
                    <span className="text-sm text-gray-500">
                      Available 24 hours after immediate recall
                    </span>
                  );
                }
              })()
            )}
          </div>
        </div>
      )}

      {/* Available Studies - Hidden for guided flow */}
      {/* Users should follow the guided study flow instead of manually joining studies */}

      {/* Debug Panel - Remove in production */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-yellow-800 mb-2">Information</h3>
        <div className="text-sm text-yellow-700">
          <p><strong>In case of technical issue contact Frank Masabo at:</strong> masabo.frank@iu-study.org</p>
          <p><strong>Or Whatsupp:</strong> +358451442401</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;