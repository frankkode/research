import { User } from '../types';

export const getStudyPhase = (user: User): string => {
  if (!user.consent_completed) return 'consent';
  if (!user.pre_quiz_completed) return 'pre_quiz';
  if (!user.interaction_completed) return 'interaction';
  if (!user.post_quiz_completed) return 'post_quiz';
  return 'completed';
};

export const getNextAction = (user: User): { action: string; description: string; route?: string } => {
  const phase = getStudyPhase(user);
  
  switch (phase) {
    case 'consent':
      return {
        action: 'Complete Consent Form',
        description: 'Review and agree to participate in the study',
        route: '/consent'
      };
    case 'pre_quiz':
      return {
        action: 'Take Pre-Assessment',
        description: 'Test your current Linux knowledge',
        route: '/quiz/pre'
      };
    case 'interaction':
      return {
        action: 'Start Learning Session',
        description: user.study_group === 'CHATGPT' 
          ? 'Begin ChatGPT learning session'
          : 'Begin PDF reading session',
        route: '/study/start'
      };
    case 'post_quiz':
      return {
        action: 'Take Post-Assessment',
        description: 'Test your Linux knowledge after learning',
        route: '/quiz/post'
      };
    case 'completed':
      return {
        action: 'Study Complete',
        description: 'Thank you for participating in the study!'
      };
    default:
      return {
        action: 'Continue Study',
        description: 'Continue with your study session'
      };
  }
};

export const canStartSession = (user: User): boolean => {
  return user.consent_completed && user.pre_quiz_completed && !user.interaction_completed;
};

export const getSessionTimeRemaining = (startTime: string, durationMinutes: number): number => {
  const start = new Date(startTime).getTime();
  const now = Date.now();
  const elapsed = now - start;
  const maxDuration = durationMinutes * 60 * 1000;
  const remaining = maxDuration - elapsed;
  
  return Math.max(0, Math.floor(remaining / 1000)); // Return seconds remaining
};

export const formatStudyTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export const getProgressPercentage = (user: User): number => {
  const steps = [
    user.consent_completed,
    user.pre_quiz_completed,
    user.interaction_completed,
    user.post_quiz_completed
  ];
  
  const completed = steps.filter(Boolean).length;
  return Math.round((completed / steps.length) * 100);
};

export const isStudyComplete = (user: User): boolean => {
  return user.study_completed && user.post_quiz_completed;
};

export const getStudyGroupColor = (studyGroup: string): string => {
  switch (studyGroup) {
    case 'CHATGPT':
      return 'blue';
    case 'PDF':
      return 'green';
    default:
      return 'gray';
  }
};

export const getStudyGroupIcon = (studyGroup: string): string => {
  switch (studyGroup) {
    case 'CHATGPT':
      return 'chat';
    case 'PDF':
      return 'document';
    default:
      return 'book';
  }
};

export const validateSessionAccess = (user: User, sessionId: string): boolean => {
  // Check if user can access this session
  if (!canStartSession(user)) {
    return false;
  }
  
  // Additional validation logic can be added here
  return true;
};

export const getSessionInstructions = (studyGroup: string): string[] => {
  const commonInstructions = [
    'You have 30 minutes to complete this learning session',
    'Your interactions are being recorded for research purposes',
    'You can finish the session early by clicking the "Finish Session" button',
    'The session will automatically end when the timer reaches zero'
  ];
  
  const specificInstructions = studyGroup === 'CHATGPT' 
    ? ['Ask questions about the 10 Linux commands listed in the chat interface']
    : ['Read through the PDF document and study the Linux commands'];
  
  return [...commonInstructions, ...specificInstructions];
};

export const generateParticipantId = (): string => {
  const timestamp = Date.now().toString().slice(-6);
  const randomSuffix = Math.random().toString(36).substr(2, 3).toUpperCase();
  return `P${timestamp}${randomSuffix}`;
};

export const assignRandomGroup = (): 'PDF' | 'CHATGPT' => {
  return Math.random() < 0.5 ? 'PDF' : 'CHATGPT';
};