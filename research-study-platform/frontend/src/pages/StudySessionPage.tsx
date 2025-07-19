import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import StudySession from '../components/study/StudySession';

const StudySessionPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { user } = useAuth();

  // Redirect if no session ID or user not in interaction phase
  if (!sessionId || !user?.interaction_completed === false) {
    return <Navigate to="/dashboard" replace />;
  }

  return <StudySession sessionId={sessionId} />;
};

export default StudySessionPage;