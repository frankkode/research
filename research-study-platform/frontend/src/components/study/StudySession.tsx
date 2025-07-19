import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { studyApi, authApi, chatApi } from '../../services/api';
import { StudySession as StudySessionType } from '../../types';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../common/LoadingSpinner';
import Timer from '../common/Timer';
import ChatInterface from '../chat/ChatInterface';
import PDFViewer from '../pdf/PDFViewer';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  BookOpenIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';

interface StudySessionProps {
  sessionId?: string;
}

const StudySession: React.FC<StudySessionProps> = ({ sessionId: propSessionId }) => {
  const { sessionId: paramSessionId } = useParams<{ sessionId: string }>();
  const sessionId = propSessionId || paramSessionId;
  const { user, refreshUser } = useAuth();
  const navigate = useNavigate();
  
  const [session, setSession] = useState<StudySessionType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeExpired, setTimeExpired] = useState(false);
  const [sessionStartTime] = useState(Date.now());
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [timeSpent, setTimeSpent] = useState(0); // Actual time spent (paused time excluded)
  const [lastActiveTime, setLastActiveTime] = useState(Date.now());
  const [interactionStats, setInteractionStats] = useState({
    totalTime: 0,
    pagesVisited: 0,
    messagesExchanged: 0
  });

  const SESSION_DURATION_MINUTES = 30; // Still keep as max, but allow early completion

  useEffect(() => {
    if (sessionId) {
      loadSession();
    }
  }, [sessionId]);

  // Track time spent while session is active
  useEffect(() => {
    if (!isPaused && sessionId) {
      const interval = setInterval(() => {
        const now = Date.now();
        const timeDiff = Math.floor((now - lastActiveTime) / 1000);
        
        if (timeDiff >= 1) {
          setTimeSpent(prev => prev + timeDiff);
          setLastActiveTime(now);
        }
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isPaused, sessionId, lastActiveTime]);

  // Save time spent to backend periodically
  useEffect(() => {
    if (sessionId && timeSpent > 0) {
      const interval = setInterval(() => {
        studyApi.updateSessionTime(sessionId, {
          time_spent: timeSpent,
          is_paused: isPaused
        }).catch(error => {
          console.error('Failed to update session time:', error);
        });
      }, 10000); // Update every 10 seconds

      return () => clearInterval(interval);
    }
  }, [sessionId, timeSpent, isPaused]);

  // Save session state before user leaves the page
  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (sessionId && timeSpent > 0) {
        // Try to save the final state
        studyApi.updateSessionTime(sessionId, {
          time_spent: timeSpent,
          is_paused: isPaused
        }).catch(error => {
          console.error('Failed to save session state before unload:', error);
        });
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [sessionId, timeSpent, isPaused]);

  const loadSession = async () => {
    if (!sessionId) return;
    
    try {
      setIsLoading(true);
      const response = await studyApi.getSession(sessionId);
      const sessionData = response.data;
      
      // Check if user has permission to access this session
      if (sessionData.user !== user?.id) {
        toast.error('You do not have permission to access this session');
        navigate('/dashboard');
        return;
      }
      
      // Check if session is already completed
      if (sessionData.is_completed) {
        toast('This session has already been completed', {
          icon: 'ℹ️',
          style: {
            background: '#dbeafe',
            color: '#1e40af',
          },
        });
        navigate('/dashboard');
        return;
      }
      
      setSession(sessionData);
      
      // Load existing time spent from session data
      if (sessionData.interaction_duration) {
        setTimeSpent(sessionData.interaction_duration);
      }
      
      // Check if session needs to be moved to interaction phase
      if (sessionData.current_phase !== 'interaction' && sessionData.current_phase !== 'post_quiz' && sessionData.current_phase !== 'completed') {
        console.log(`Session is in "${sessionData.current_phase}" phase, moving to interaction phase...`);
        try {
          await studyApi.updatePhase(sessionId, 'interaction');
          console.log('Session moved to interaction phase');
          
          // Reload session data to get updated phase
          const updatedSession = await studyApi.getSession(sessionId);
          setSession(updatedSession.data);
        } catch (error) {
          console.error('Failed to update session phase to interaction:', error);
        }
      }
      
      // Optional: Check if session has expired based on start time (but don't enforce)
      const sessionStart = new Date(sessionData.session_started_at).getTime();
      const elapsed = Date.now() - sessionStart;
      const maxDuration = SESSION_DURATION_MINUTES * 60 * 1000;
      
      if (elapsed >= maxDuration) {
        // Don't force expiration, just show warning
        console.warn('Session has exceeded the recommended 30-minute duration');
      }
      
    } catch (error) {
      toast.error('Failed to load session');
      navigate('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionExpired = async () => {
    if (!sessionId) return;
    
    try {
      await studyApi.completeSession(sessionId);
      await studyApi.updatePhase(sessionId, 'completed');
      toast.error('Session time has expired');
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to complete expired session:', error);
    }
  };

  const handleTimeUp = () => {
    // Don't force expiration, just show notification
    toast('Session time limit reached. You can continue or finish when ready.', {
      duration: 10000,
      icon: '⏰',
      style: {
        background: '#fbbf24',
        color: '#92400e',
      },
    });
  };

  const handleTimeWarning = (minutesRemaining: number) => {
    // Log warning event
    if (sessionId) {
      studyApi.logEvent({
        session_id: sessionId,
        log_type: 'system_event',
        event_data: {
          event: 'time_warning',
          minutes_remaining: minutesRemaining,
          timestamp: new Date().toISOString()
        }
      });
    }
  };

  const handlePause = () => {
    setIsPaused(true);
    // Update backend with current time spent
    if (sessionId) {
      studyApi.updateSessionTime(sessionId, {
        time_spent: timeSpent,
        is_paused: true
      }).catch(error => {
        console.error('Failed to update session time:', error);
      });
    }
  };

  const handleResume = () => {
    setIsPaused(false);
    setLastActiveTime(Date.now()); // Reset the active time counter
    // Log resume event
    if (sessionId) {
      studyApi.logEvent({
        session_id: sessionId,
        log_type: 'system_event',
        event_data: {
          event: 'session_resumed',
          timestamp: new Date().toISOString()
        }
      });
    }
  };

  const handleInteractionUpdate = useCallback((totalTime: number, pagesVisited: number) => {
    setInteractionStats(prev => ({
      ...prev,
      totalTime,
      pagesVisited
    }));
  }, []);

  const handleChatUpdate = useCallback((messagesExchanged: number) => {
    setInteractionStats(prev => ({
      ...prev,
      messagesExchanged
    }));
  }, []);

  const handleFinishSession = async () => {
    if (!sessionId || isSubmitting) return;
    
    try {
      setIsSubmitting(true);
      console.log('Starting session finish process...');
      console.log('Current session state:', session);
      console.log('Current user state:', user);
      
      // Log completion event
      await studyApi.logEvent({
        session_id: sessionId,
        log_type: 'system_event',
        event_data: {
          event: 'session_finished_early',
          interaction_stats: interactionStats,
          timestamp: new Date().toISOString(),
          manual_completion: true,
          current_phase: session?.current_phase
        }
      });
      console.log('Event logged successfully');
      
      // End the chat session if it's a ChatGPT session
      if (user?.study_group === 'CHATGPT') {
        try {
          await chatApi.endSession(sessionId);
          console.log('Chat session ended');
        } catch (error) {
          console.warn('Failed to end chat session:', error);
        }
      }
      
      // ONLY update phase to post_quiz - this should mark interaction as completed
      console.log(`Updating phase from "${session?.current_phase}" to "post_quiz"...`);
      console.log('Current session state before phase update:', {
        current_phase: session?.current_phase,
        is_completed: session?.is_completed,
        is_active: session?.is_active,
        session_id: session?.session_id
      });
      
      // Force refresh session data to get the latest phase
      console.log('Refreshing session data before phase update...');
      try {
        const freshSession = await studyApi.getSession(sessionId);
        setSession(freshSession.data);
        console.log('Fresh session data:', {
          current_phase: freshSession.data.current_phase,
          is_completed: freshSession.data.is_completed,
          is_active: freshSession.data.is_active
        });
      } catch (error) {
        console.error('Failed to refresh session data:', error);
      }
      
      // Use the fresh session data
      const currentPhase = session?.current_phase;
      console.log(`Using current phase: "${currentPhase}" for phase update`);
      
      // Handle different starting phases appropriately
      if (currentPhase === 'post_quiz') {
        console.log('Session is already in post_quiz phase. This should not happen when finishing learning session.');
        console.log('Skipping phase update to avoid marking post_quiz as completed.');
        // Do nothing - session is already in the correct phase
      } else if (currentPhase === 'interaction') {
        console.log('Session is in interaction phase, moving to post_quiz...');
        const phaseUpdateResponse = await studyApi.updatePhase(sessionId, 'post_quiz');
        console.log('Phase updated successfully:', phaseUpdateResponse.data);
      } else {
        console.log(`Session is in "${currentPhase}" phase, moving to interaction first...`);
        await studyApi.updatePhase(sessionId, 'interaction');
        console.log('Session moved to interaction phase');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        console.log('Now moving to post_quiz...');
        const phaseUpdateResponse = await studyApi.updatePhase(sessionId, 'post_quiz');
        console.log('Phase updated successfully:', phaseUpdateResponse.data);
      }
      
      // Wait a moment for the backend to process the change
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // FAILSAFE: Directly mark interaction as completed via API
      console.log('FAILSAFE: Directly marking interaction as completed...');
      try {
        await authApi.completeInteraction();
        console.log('Direct interaction completion called successfully');
      } catch (error) {
        console.error('Failed to directly complete interaction:', error);
      }
      
      // Refresh user data to get the updated completion status
      console.log('Refreshing user data...');
      const updatedUser = await refreshUser();
      console.log('User data refreshed:', updatedUser);
      
      // Wait another moment to ensure the user state is updated
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Get fresh user data directly from API to verify
      try {
        console.log('Fetching fresh user data from API...');
        const freshUserResponse = await authApi.getProfile();
        console.log('Fresh user data from API:', {
          interaction_completed: freshUserResponse.data.interaction_completed,
          consent_completed: freshUserResponse.data.consent_completed,
          pre_quiz_completed: freshUserResponse.data.pre_quiz_completed,
          post_quiz_completed: freshUserResponse.data.post_quiz_completed,
          study_completed: freshUserResponse.data.study_completed,
          completion_percentage: freshUserResponse.data.completion_percentage
        });
        
        // Force update user state in localStorage
        const updatedUser = freshUserResponse.data;
        localStorage.setItem('user', JSON.stringify(updatedUser));
        console.log('Updated user state in localStorage');
        
      } catch (error) {
        console.error('Failed to get fresh user data:', error);
      }
      
      // Log the current user state before navigating
      console.log('Final user state before navigation:', {
        interaction_completed: user?.interaction_completed,
        consent_completed: user?.consent_completed,
        pre_quiz_completed: user?.pre_quiz_completed,
        post_quiz_completed: user?.post_quiz_completed
      });
      
      toast.success('Learning session completed! Moving to post-quiz...');
      navigate('/dashboard');
    } catch (error) {
      console.error('Failed to complete session:', error);
      toast.error('Failed to complete session');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getSessionTitle = () => {
    if (!user) return 'Study Session';
    return user.study_group === 'CHATGPT' 
      ? 'ChatGPT Learning Session' 
      : 'PDF Learning Session';
  };

  const getSessionDescription = () => {
    if (!user) return '';
    return user.study_group === 'CHATGPT'
      ? 'Learn Linux commands through interactive conversation with ChatGPT'
      : 'Study Linux commands from the provided PDF document';
  };

  const getSessionIcon = () => {
    if (!user) return <BookOpenIcon className="h-6 w-6" />;
    return user.study_group === 'CHATGPT' 
      ? <ChatBubbleLeftRightIcon className="h-6 w-6" />
      : <BookOpenIcon className="h-6 w-6" />;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (timeExpired) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <LockClosedIcon className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Session Expired</h2>
          <p className="text-gray-600 mb-6">
            Your 30-minute study session has expired. Please return to the dashboard to continue with the next phase.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn btn-primary w-full"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Session Not Found</h2>
          <p className="text-gray-600 mb-4">The requested session could not be found.</p>
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

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Session Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                user?.study_group === 'CHATGPT' ? 'bg-blue-100' : 'bg-green-100'
              }`}>
                <div className={user?.study_group === 'CHATGPT' ? 'text-blue-600' : 'text-green-600'}>
                  {getSessionIcon()}
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {getSessionTitle()}
                </h1>
                <p className="text-gray-600">
                  {getSessionDescription()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Session Stats */}
              <div className="text-right">
                <div className="text-sm text-gray-500">Session Progress</div>
                <div className="text-lg font-semibold text-gray-900">
                  {user?.study_group === 'CHATGPT' 
                    ? `${interactionStats.messagesExchanged} messages`
                    : `${interactionStats.pagesVisited} pages read`}
                </div>
                <div className="text-sm text-gray-500">
                  Active time: {Math.floor(timeSpent / 60)}:{(timeSpent % 60).toString().padStart(2, '0')}
                </div>
              </div>
              
              <button
                onClick={handleFinishSession}
                disabled={isSubmitting}
                className="btn btn-outline flex items-center space-x-2 disabled:opacity-50"
              >
                <CheckCircleIcon className="h-5 w-5" />
                <span>{isSubmitting ? 'Finishing...' : 'Finish Session'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Timer */}
        <div className="mb-6">
          <Timer
            durationMinutes={SESSION_DURATION_MINUTES}
            onTimeUp={handleTimeUp}
            onWarning={handleTimeWarning}
            onPause={handlePause}
            onResume={handleResume}
            isPaused={isPaused}
          />
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-lg h-[600px]">
          {user?.study_group === 'CHATGPT' ? (
            sessionId ? (
              <ChatInterface
                sessionId={sessionId}
                onSessionUpdate={(chatSession: any) => {
                  handleChatUpdate(chatSession.total_messages);
                }}
              />
            ) : (
              <div className="p-6 text-center">
                <p className="text-gray-500">Session not found</p>
              </div>
            )
          ) : (
            sessionId ? (
              <PDFViewer
                sessionId={sessionId}
                onInteractionUpdate={handleInteractionUpdate}
              />
            ) : (
              <div className="p-6 text-center">
                <p className="text-gray-500">Session not found</p>
              </div>
            )
          )}
        </div>

        {/* Session Guidelines */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <ClockIcon className="h-5 w-5 text-blue-600 mt-0.5" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Session Guidelines
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>You have up to 30 minutes to complete this learning session</li>
                  <li>
                    {user?.study_group === 'CHATGPT' 
                      ? 'Ask questions about the 10 Linux commands listed in the chat interface'
                      : 'Read through the PDF document and study the Linux commands'}
                  </li>
                  <li>Your interactions are being recorded for research purposes</li>
                  <li>You can pause and resume the session at any time using the timer controls</li>
                  <li>You can finish the session early by clicking the "Finish Session" button</li>
                  <li>The session will warn you when time is running out, but you can continue if needed</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudySession;