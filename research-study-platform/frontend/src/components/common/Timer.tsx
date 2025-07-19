import React, { useState, useEffect, useCallback } from 'react';
import { ClockIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface TimerProps {
  durationMinutes: number;
  onTimeUp: () => void;
  onWarning?: (minutesRemaining: number) => void;
  onPause?: () => void;
  onResume?: () => void;
  isPaused?: boolean;
  className?: string;
}

const Timer: React.FC<TimerProps> = ({ 
  durationMinutes, 
  onTimeUp, 
  onWarning, 
  onPause,
  onResume,
  isPaused: externalPaused = false,
  className = '' 
}) => {
  const [timeRemaining, setTimeRemaining] = useState(durationMinutes * 60); // in seconds
  const [isActive, setIsActive] = useState(true);
  const [warningShown, setWarningShown] = useState({ fiveMin: false, oneMin: false });

  const formatTime = useCallback((seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }, []);

  const getTimeColor = useCallback((seconds: number) => {
    if (seconds <= 60) return 'text-red-600'; // Last minute
    if (seconds <= 300) return 'text-orange-600'; // Last 5 minutes
    if (seconds <= 600) return 'text-yellow-600'; // Last 10 minutes
    return 'text-gray-700';
  }, []);

  const getProgressPercentage = useCallback(() => {
    const totalSeconds = durationMinutes * 60;
    return ((totalSeconds - timeRemaining) / totalSeconds) * 100;
  }, [durationMinutes, timeRemaining]);

  useEffect(() => {
    let interval: NodeJS.Timer;

    if (isActive && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          const newTime = prev - 1;
          
          // Check for warnings
          if (newTime === 300 && !warningShown.fiveMin) { // 5 minutes
            setWarningShown(prev => ({ ...prev, fiveMin: true }));
            toast('5 minutes remaining!', {
              duration: 5000,
              icon: '⏰',
              style: {
                background: '#fbbf24',
                color: '#92400e',
              },
            });
            onWarning?.(5);
          }
          
          if (newTime === 60 && !warningShown.oneMin) { // 1 minute
            setWarningShown(prev => ({ ...prev, oneMin: true }));
            toast.error('1 minute remaining!', {
              duration: 5000,
              icon: '⚠️',
            });
            onWarning?.(1);
          }
          
          if (newTime === 0) {
            setIsActive(false);
            toast.error('Time is up!', {
              duration: 10000,
              icon: '⏰',
            });
            onTimeUp();
          }
          
          return newTime;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isActive, timeRemaining, warningShown, onTimeUp, onWarning]);

  const pause = () => {
    setIsActive(false);
    onPause?.();
  };
  
  const resume = () => {
    setIsActive(true);
    onResume?.();
  };

  // Sync with external pause state
  useEffect(() => {
    setIsActive(!externalPaused);
  }, [externalPaused]);

  const minutesRemaining = Math.floor(timeRemaining / 60);
  const isUrgent = timeRemaining <= 300; // Last 5 minutes

  return (
    <div className={`${className}`}>
      <div className={`flex items-center space-x-3 p-4 rounded-lg border ${
        isUrgent ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-white'
      }`}>
        <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
          isUrgent ? 'bg-red-100' : 'bg-gray-100'
        }`}>
          {isUrgent ? (
            <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />
          ) : (
            <ClockIcon className="h-5 w-5 text-gray-600" />
          )}
        </div>
        
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              Time Remaining
            </span>
            <span className={`text-2xl font-bold ${getTimeColor(timeRemaining)}`}>
              {formatTime(timeRemaining)}
            </span>
          </div>
          
          {/* Progress bar */}
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-1000 ${
                isUrgent ? 'bg-red-500' : 'bg-blue-500'
              }`}
              style={{ width: `${getProgressPercentage()}%` }}
            />
          </div>
          
          <div className="mt-1 text-xs text-gray-500">
            {minutesRemaining} minutes left of {durationMinutes} minutes total
          </div>
        </div>
        
        {/* Pause/Resume controls (optional) */}
        <div className="flex space-x-2">
          {isActive ? (
            <button
              onClick={pause}
              className="px-3 py-1 text-xs text-gray-600 hover:text-gray-800 border border-gray-300 rounded hover:bg-gray-50"
            >
              Pause
            </button>
          ) : (
            <button
              onClick={resume}
              className="px-3 py-1 text-xs text-blue-600 hover:text-blue-800 border border-blue-300 rounded hover:bg-blue-50"
            >
              Resume
            </button>
          )}
        </div>
      </div>
      
      {/* Warning messages */}
      {timeRemaining <= 60 && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-4 w-4 text-red-600 mr-2" />
            <span className="text-sm text-red-700 font-medium">
              Less than 1 minute remaining! Please wrap up your session.
            </span>
          </div>
        </div>
      )}
      
      {timeRemaining <= 300 && timeRemaining > 60 && (
        <div className="mt-2 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="flex items-center">
            <ClockIcon className="h-4 w-4 text-orange-600 mr-2" />
            <span className="text-sm text-orange-700 font-medium">
              {minutesRemaining} minutes remaining. Please prepare to finish.
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Timer;