import axios from 'axios';
import { 
  AuthResponse, 
  User, 
  Study, 
  StudySession, 
  ChatSession, 
  ChatInteraction, 
  ChatMessage, 
  ChatResponse, 
  Quiz, 
  QuizAttempt, 
  LoginCredentials, 
  RegisterData, 
  CostLimits
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (data: RegisterData) => 
    api.post<AuthResponse>('/auth/register/', data),
  
  login: (data: LoginCredentials) =>
    api.post<AuthResponse>('/auth/login/', data),
  
  logout: () => api.post('/auth/logout/'),
  
  getProfile: () => api.get<User>('/auth/profile/'),
  
  submitConsent: (agreed: boolean) => 
    api.post('/auth/consent/', { agreed }),
  
  completeInteraction: () => 
    api.post('/auth/complete-interaction/'),
};

export const studyApi = {
  getActiveStudies: () => api.get<Study[]>('/studies/active/'),
  
  joinStudy: (studyId: string) =>
    api.post<StudySession>(`/studies/join/${studyId}/`),
  
  createOrGetSession: (data: { user_agent: string }) =>
    api.post<StudySession>('/studies/session/create/', data),
  
  getMySessions: () => api.get<StudySession[]>('/studies/my-sessions/'),
  
  getSession: (sessionId: string) => 
    api.get<StudySession>(`/studies/session/${sessionId}/`),
  
  logEvent: (data: {
    session_id: string;
    log_type: string;
    event_data: any;
  }) => api.post('/studies/log-event/', data),
  
  updatePhase: (sessionId: string, phase: string) =>
    api.put(`/studies/session/${sessionId}/phase/`, { phase }),
  
  completeSession: (sessionId: string) =>
    api.post(`/studies/session/${sessionId}/complete/`),
  
  updateSessionTime: (sessionId: string, data: { time_spent: number; is_paused: boolean }) =>
    api.post(`/studies/session/${sessionId}/time/`, data),
};

export const chatApi = {
  startSession: (sessionId: string) =>
    api.post<ChatSession>(`/chats/session/${sessionId}/start/`),
  
  endSession: (sessionId: string) =>
    api.post<ChatSession>(`/chats/session/${sessionId}/end/`),
  
  getSession: (sessionId: string) =>
    api.get<ChatSession>(`/chats/session/${sessionId}/`),
  
  sendMessage: (message: ChatMessage) =>
    api.post<ChatResponse>('/chats/send/', message),
  
  getHistory: (sessionId: string) =>
    api.get<ChatInteraction[]>(`/chats/history/${sessionId}/`),
  
  getCostLimits: () =>
    api.get<CostLimits>('/chats/costs/my-limits/'),
};

export const quizApi = {
  getQuiz: (quizId: string) => api.get<Quiz>(`/quizzes/${quizId}/`),
  
  getQuizByType: (quizType: string) => api.get<Quiz>(`/quizzes/type/${quizType}/`),
  
  startQuiz: (quizId: string, sessionId: string) =>
    api.post<QuizAttempt>(`/quizzes/${quizId}/start/`, { session_id: sessionId }),
  
  submitAnswer: (attemptId: string, data: {
    question_id: string;
    selected_choice?: string;
    text_answer?: string;
  }) => api.post(`/quizzes/attempt/${attemptId}/answer/`, data),
  
  submitQuiz: (attemptId: string) =>
    api.post<QuizAttempt>(`/quizzes/attempt/${attemptId}/submit/`),
  
  submitQuizResults: (data: {
    quiz_type: string;
    score: number;
    total_questions: number;
    correct_answers: number;
    time_taken_seconds: number;
    answers: any[];
  }) => api.post('/quizzes/submit-results/', data),
  
  getMyAttempts: () => api.get<QuizAttempt[]>('/quizzes/my-attempts/'),
};

export const pdfApi = {
  getDocuments: () => api.get('/pdfs/documents/'),
  
  logInteraction: (data: {
    session_id: string;
    document_id: string;
    interaction_type: string;
    page_number?: number;
    time_on_page_seconds?: number;
    scroll_depth_percentage?: number;
    annotations_made?: number;
  }) => api.post('/pdfs/log-interaction/', data),
  
  getSession: (sessionId: string) =>
    api.get(`/pdfs/session/${sessionId}/`),
  
  startSession: (sessionId: string, documentId: string) =>
    api.post(`/pdfs/session/${sessionId}/start/`, { document_id: documentId }),
};

export const coreApi = {
  healthCheck: () => api.get('/core/health/'),
};

export const researchApi = {
  getStudies: () => api.get('/research/studies/'),
  
  getStudyAnalytics: (studyId: string) => 
    api.get(`/research/studies/${studyId}/analytics/`),
  
  getStudyParticipants: (studyId: string) => 
    api.get(`/research/studies/${studyId}/participants/`),
  
  getAllParticipants: () => 
    api.get('/research/participants/all/'),
  
  getDashboardOverview: () => 
    api.get('/research/dashboard/overview/'),
  
  getActivityTimeline: (days: number = 30) => 
    api.get(`/research/dashboard/activity_timeline/?days=${days}`),
  
  exportParticipantData: (studyId: string, format: string = 'csv') =>
    api.post('/research/exports/export_participant_data/', { 
      study_id: studyId, 
      format 
    }),
  
  exportAllData: () => api.get('/research/export/all/'),
  
  exportChatInteractions: () => api.get('/research/export/chat/'),
  
  exportPDFInteractions: () => api.get('/research/export/pdf/'),
  
  exportQuizResponses: () => api.get('/research/export/quiz/'),
  
  getStudyStatistics: () => api.get('/research/statistics/'),
  
  getLearningEffectivenessData: () => api.get('/research/dashboard/learning_effectiveness/'),
};

export default api;