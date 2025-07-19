import { QuizAttempt, QuizResponse, QuizResult } from '../types';

export interface QuizExportData {
  participant_id: string;
  study_group: string;
  quiz_type: string;
  attempt_id: string;
  started_at: string;
  completed_at: string;
  total_time_seconds: number;
  score_percentage: number;
  correct_answers: number;
  total_questions: number;
  responses: QuizResponseExport[];
}

export interface QuizResponseExport {
  question_id: string;
  question_text: string;
  question_category: string;
  question_difficulty: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  time_taken_seconds: number;
  response_timestamp: string;
}

export const exportQuizData = (
  attempt: QuizAttempt,
  result: QuizResult,
  participantId: string,
  studyGroup: string
): QuizExportData => {
  const responses: QuizResponseExport[] = result.question_results.map(qr => ({
    question_id: qr.question.id,
    question_text: qr.question.question_text,
    question_category: qr.question.category || 'uncategorized',
    question_difficulty: qr.question.difficulty || 'medium',
    selected_answer: qr.question.choices.find(c => c.id === qr.response.selected_choice)?.choice_text || '',
    correct_answer: qr.correct_answer.choice_text,
    is_correct: qr.is_correct,
    time_taken_seconds: qr.response.time_taken_seconds,
    response_timestamp: qr.response.created_at
  }));

  return {
    participant_id: participantId,
    study_group: studyGroup,
    quiz_type: attempt.quiz,
    attempt_id: attempt.id,
    started_at: attempt.started_at,
    completed_at: attempt.completed_at || '',
    total_time_seconds: attempt.time_taken_seconds,
    score_percentage: attempt.score || 0,
    correct_answers: attempt.correct_answers,
    total_questions: attempt.total_questions,
    responses
  };
};

export const exportToCSV = (data: QuizExportData[]): string => {
  if (data.length === 0) return '';

  // Headers for main quiz data
  const headers = [
    'participant_id',
    'study_group',
    'quiz_type',
    'attempt_id',
    'started_at',
    'completed_at',
    'total_time_seconds',
    'score_percentage',
    'correct_answers',
    'total_questions'
  ];

  // Headers for response data
  const responseHeaders = [
    'question_id',
    'question_text',
    'question_category',
    'question_difficulty',
    'selected_answer',
    'correct_answer',
    'is_correct',
    'time_taken_seconds',
    'response_timestamp'
  ];

  let csv = headers.join(',') + '\n';

  data.forEach(attempt => {
    const row = [
      attempt.participant_id,
      attempt.study_group,
      attempt.quiz_type,
      attempt.attempt_id,
      attempt.started_at,
      attempt.completed_at,
      attempt.total_time_seconds,
      attempt.score_percentage,
      attempt.correct_answers,
      attempt.total_questions
    ];
    csv += row.join(',') + '\n';
  });

  // Add response data
  csv += '\n' + responseHeaders.join(',') + '\n';

  data.forEach(attempt => {
    attempt.responses.forEach(response => {
      const row = [
        response.question_id,
        `"${response.question_text.replace(/"/g, '""')}"`,
        response.question_category,
        response.question_difficulty,
        `"${response.selected_answer.replace(/"/g, '""')}"`,
        `"${response.correct_answer.replace(/"/g, '""')}"`,
        response.is_correct,
        response.time_taken_seconds,
        response.response_timestamp
      ];
      csv += row.join(',') + '\n';
    });
  });

  return csv;
};

export const exportToJSON = (data: QuizExportData[]): string => {
  return JSON.stringify(data, null, 2);
};

export const downloadFile = (content: string, filename: string, contentType: string) => {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

export const generateQuizStatistics = (data: QuizExportData[]) => {
  const stats = {
    totalParticipants: data.length,
    averageScore: 0,
    averageTime: 0,
    categoryPerformance: {} as Record<string, { correct: number; total: number }>,
    difficultyPerformance: {} as Record<string, { correct: number; total: number }>,
    studyGroupComparison: {} as Record<string, { 
      participants: number; 
      averageScore: number; 
      averageTime: number; 
    }>
  };

  if (data.length === 0) return stats;

  // Calculate overall statistics
  const totalScore = data.reduce((sum, attempt) => sum + attempt.score_percentage, 0);
  const totalTime = data.reduce((sum, attempt) => sum + attempt.total_time_seconds, 0);
  
  stats.averageScore = Math.round(totalScore / data.length);
  stats.averageTime = Math.round(totalTime / data.length);

  // Calculate category performance
  data.forEach(attempt => {
    attempt.responses.forEach(response => {
      const category = response.question_category;
      if (!stats.categoryPerformance[category]) {
        stats.categoryPerformance[category] = { correct: 0, total: 0 };
      }
      stats.categoryPerformance[category].total++;
      if (response.is_correct) {
        stats.categoryPerformance[category].correct++;
      }
    });
  });

  // Calculate difficulty performance
  data.forEach(attempt => {
    attempt.responses.forEach(response => {
      const difficulty = response.question_difficulty;
      if (!stats.difficultyPerformance[difficulty]) {
        stats.difficultyPerformance[difficulty] = { correct: 0, total: 0 };
      }
      stats.difficultyPerformance[difficulty].total++;
      if (response.is_correct) {
        stats.difficultyPerformance[difficulty].correct++;
      }
    });
  });

  // Calculate study group comparison
  data.forEach(attempt => {
    const group = attempt.study_group;
    if (!stats.studyGroupComparison[group]) {
      stats.studyGroupComparison[group] = { 
        participants: 0, 
        averageScore: 0, 
        averageTime: 0 
      };
    }
    stats.studyGroupComparison[group].participants++;
  });

  // Calculate averages for each group
  Object.keys(stats.studyGroupComparison).forEach(group => {
    const groupData = data.filter(attempt => attempt.study_group === group);
    const groupScore = groupData.reduce((sum, attempt) => sum + attempt.score_percentage, 0);
    const groupTime = groupData.reduce((sum, attempt) => sum + attempt.total_time_seconds, 0);
    
    stats.studyGroupComparison[group].averageScore = Math.round(groupScore / groupData.length);
    stats.studyGroupComparison[group].averageTime = Math.round(groupTime / groupData.length);
  });

  return stats;
};

export const formatTimeForExport = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};