export interface User {
  id: string;
  email: string;
  username: string;
  participant_id: string;
  study_group: 'PDF' | 'CHATGPT';
  consent_completed: boolean;
  pre_quiz_completed: boolean;
  interaction_completed: boolean;
  post_quiz_completed: boolean;
  study_completed: boolean;
  completion_percentage: number;
  created_at: string;
  consent_completed_at?: string;
  pre_quiz_completed_at?: string;
  interaction_completed_at?: string;
  post_quiz_completed_at?: string;
  study_completed_at?: string;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface UserProfile {
  age?: number;
  gender?: string;
  education_level?: string;
  consent_given: boolean;
  consent_timestamp?: string;
}

export interface Study {
  id: string;
  title: string;
  description: string;
  is_active: boolean;
  max_participants: number;
  duration_minutes: number;
}

export interface StudySession {
  id: string;
  user: string;
  session_id: string;
  current_phase: 'consent' | 'demographics' | 'pre_quiz' | 'interaction' | 'post_quiz' | 'completed';
  session_started_at: string;
  session_ended_at?: string;
  interaction_duration?: number;
  is_active: boolean;
  is_completed: boolean;
}

export interface ChatSession {
  id: string;
  session: string;
  user: string;
  chat_started_at: string;
  chat_ended_at?: string;
  total_messages: number;
  total_tokens_used: number;
  total_estimated_cost_usd: number;
  linux_command_queries: number;
  average_response_time_ms: number;
  rate_limit_hits: number;
  total_chat_duration_seconds?: number;
}

export interface ChatInteraction {
  id: string;
  session: string;
  user: string;
  message_type: 'user' | 'assistant';
  conversation_turn: number;
  user_message?: string;
  assistant_response?: string;
  error_message?: string;
  response_time_ms?: number;
  total_tokens?: number;
  estimated_cost_usd?: number;
  contains_linux_command: boolean;
  rate_limit_hit: boolean;
  message_timestamp: string;
}

export interface ChatMessage {
  message: string;
  session_id: string;
  conversation_turn: number;
}

export interface ChatResponse {
  user_message: string;
  assistant_response: string;
  response_time_ms: number;
  total_tokens: number;
  conversation_turn: number;
  interaction_id: string;
}

export interface Quiz {
  id: string;
  title: string;
  description: string;
  quiz_type: 'immediate_recall' | 'transfer' | 'pre_assessment';
  time_limit_minutes: number;
  questions: Question[];
  can_retake: boolean;
  max_attempts: number;
}

export interface Question {
  id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'text' | 'scale';
  order: number;
  is_required: boolean;
  choices: QuestionChoice[];
  correct_answer_id?: string;
  explanation?: string;
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
}

export interface QuestionChoice {
  id: string;
  choice_text: string;
  order: number;
  is_correct: boolean;
}

export interface QuizAttempt {
  id: string;
  quiz: string;
  user: string;
  session: string;
  started_at: string;
  completed_at?: string;
  is_completed: boolean;
  score?: number;
  total_questions: number;
  correct_answers: number;
  time_taken_seconds: number;
  answers: QuizResponse[];
}

export interface QuizResponse {
  id: string;
  question: string;
  selected_choice?: string;
  text_answer?: string;
  is_correct: boolean;
  time_taken_seconds: number;
  created_at: string;
}

export interface QuizResult {
  attempt: QuizAttempt;
  performance: {
    score_percentage: number;
    correct_count: number;
    total_questions: number;
    time_taken_formatted: string;
    average_time_per_question: number;
  };
  question_results: {
    question: Question;
    response: QuizResponse;
    is_correct: boolean;
    correct_answer: QuestionChoice;
  }[];
}

export interface QuizProgress {
  current_question: number;
  total_questions: number;
  answered_questions: number;
  time_elapsed: number;
  responses: Record<string, QuizResponse>;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  participant_id: string;
  study_group: 'PDF' | 'CHATGPT';
}

export interface PDFInteraction {
  id: string;
  session: string;
  user: string;
  page_number: number;
  time_on_page_seconds: number;
  scroll_depth_percentage: number;
  annotations_made: number;
  interaction_timestamp: string;
}

export interface StudyLog {
  id: string;
  session: string;
  log_type: 'page_view' | 'quiz_start' | 'quiz_submit' | 'chat_message' | 'pdf_interaction' | 'system_event';
  event_data: Record<string, any>;
  timestamp: string;
}

export interface CostLimits {
  daily_cost: number;
  weekly_cost: number;
  daily_limit_exceeded: boolean;
  weekly_limit_exceeded: boolean;
  daily_remaining: number;
  weekly_remaining: number;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  googleAuth: (token: string, studyGroup?: string) => Promise<AuthResponse & { created: boolean }>;
  logout: () => void;
  refreshUser: () => Promise<User | void>;
  isAuthenticated: boolean;
  loading: boolean;
}