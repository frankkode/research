import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Mock data
const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
  participant_id: 'P001',
  study_group: 'PDF',
  is_staff: false,
  is_superuser: false,
  study_completed: false,
};

const mockAdmin = {
  id: 2,
  username: 'admin',
  email: 'admin@example.com',
  participant_id: 'A001',
  study_group: 'PDF',
  is_staff: true,
  is_superuser: true,
  study_completed: false,
};

const mockStudy = {
  id: 1,
  name: 'Test Study',
  description: 'A test study',
  created_by: 2,
  is_active: true,
  max_participants: 100,
  participant_count: 10,
  completion_rate: 75.0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

const mockParticipant = {
  id: 1,
  user: mockUser,
  study: mockStudy,
  anonymized_id: 'P001_ABC123',
  assigned_group: 'PDF',
  consent_given: true,
  gdpr_consent: true,
  data_processing_consent: true,
  is_anonymized: false,
  withdrawn: false,
  created_at: '2024-01-01T00:00:00Z',
};

const mockQuizAttempt = {
  id: 1,
  quiz: 'pre_assessment',
  user: 1,
  session: 'session_123',
  started_at: '2024-01-01T10:00:00Z',
  completed_at: '2024-01-01T10:30:00Z',
  is_completed: true,
  score: 85,
  total_questions: 10,
  correct_answers: 8,
  time_taken_seconds: 1800,
  answers: [],
};

const mockAnalytics = {
  study_overview: {
    total_participants: 10,
    active_participants: 8,
    completion_rate: 75.0,
    average_score: 82.5,
  },
  participant_stats: {
    by_group: {
      PDF: 5,
      CHATGPT: 5,
    },
    by_status: {
      active: 8,
      completed: 2,
      withdrawn: 0,
    },
  },
  interaction_stats: {
    total_interactions: 1500,
    average_per_session: 150,
    most_common_actions: ['button_click', 'page_view', 'form_submit'],
  },
  chat_stats: {
    total_messages: 250,
    average_per_participant: 50,
    total_cost: 12.50,
  },
  pdf_stats: {
    total_page_views: 800,
    average_time_per_page: 45,
    most_viewed_pages: [1, 2, 3],
  },
  quiz_stats: {
    total_responses: 200,
    average_score: 82.5,
    completion_rate: 95.0,
  },
};

// Request handlers
const handlers = [
  // Auth endpoints
  http.post('*/api/auth/login/', async ({ request }) => {
    const body = await request.json() as any;
    if (body.username === 'admin' && body.password === 'password') {
      return HttpResponse.json({
        user: mockAdmin,
        token: 'mock-admin-token',
      });
    }
    if (body.username === 'testuser' && body.password === 'password') {
      return HttpResponse.json({
        user: mockUser,
        token: 'mock-user-token',
      });
    }
    return HttpResponse.json({ error: 'Invalid credentials' }, { status: 401 });
  }),

  http.post('*/api/auth/logout/', () => {
    return HttpResponse.json({ message: 'Logged out successfully' });
  }),

  http.get('*/api/auth/user/', () => {
    return HttpResponse.json(mockUser);
  }),

  // Study endpoints
  http.get('*/api/research/studies/', () => {
    return HttpResponse.json({
      results: [mockStudy],
      count: 1,
    });
  }),

  http.get('*/api/research/studies/:id/', ({ params }) => {
    return HttpResponse.json(mockStudy);
  }),

  http.get('*/api/research/studies/:id/analytics/', ({ params }) => {
    return HttpResponse.json(mockAnalytics);
  }),

  http.get('*/api/research/studies/:id/participants/', ({ params }) => {
    return HttpResponse.json([mockParticipant]);
  }),

  http.post('*/api/research/studies/:id/bulk-create-participants/', async ({ request }) => {
    const body = await request.json() as any;
    const count = body.participant_count || 5;
    const participants = Array.from({ length: count }, (_, i) => ({
      ...mockParticipant,
      id: i + 1,
      anonymized_id: `P${String(i + 1).padStart(3, '0')}_ABC${i + 1}`,
      assigned_group: i % 2 === 0 ? 'PDF' : 'CHATGPT',
    }));
    return HttpResponse.json(participants);
  }),

  // Participant endpoints
  http.get('*/api/research/participants/', () => {
    return HttpResponse.json({
      results: [mockParticipant],
      count: 1,
    });
  }),

  http.post('*/api/research/participants/create/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({
      ...mockParticipant,
      id: Date.now(),
      anonymized_id: `P${Date.now()}_ABC123`,
      assigned_group: body.assigned_group || 'PDF',
    });
  }),

  http.post('*/api/research/participants/:id/withdraw/', () => {
    return HttpResponse.json({
      status: 'withdrawn',
      message: 'Participant withdrawn successfully',
    });
  }),

  http.post('*/api/research/participants/:id/anonymize/', () => {
    return HttpResponse.json({
      status: 'anonymized',
      message: 'Participant anonymized successfully',
    });
  }),

  // Logging endpoints
  http.post('*/api/research/log/interaction/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({ status: 'logged', id: Date.now() });
  }),

  http.post('*/api/research/log/chat/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({ status: 'logged', id: Date.now() });
  }),

  http.post('*/api/research/log/pdf/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({ status: 'logged', id: Date.now() });
  }),

  http.post('*/api/research/log/quiz/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({ status: 'logged', id: Date.now() });
  }),

  // Quiz endpoints
  http.get('*/api/quiz/quizzes/', () => {
    return HttpResponse.json({
      results: [
        {
          id: 1,
          title: 'Pre-Assessment',
          quiz_type: 'pre_assessment',
          questions: [],
        },
      ],
    });
  }),

  http.post('*/api/quiz/attempts/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json(mockQuizAttempt);
  }),

  http.post('*/api/quiz/attempts/:id/submit/', () => {
    return HttpResponse.json({
      status: 'submitted',
      message: 'Quiz submitted successfully',
    });
  }),

  // Export endpoints
  http.post('*/api/research/export/participants/', async ({ request }) => {
    const body = await request.json() as any;
    return new HttpResponse('participant,group,status\nP001,PDF,active\n', {
      headers: {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename="participants.csv"',
      },
    });
  }),

  http.get('*/api/research/export/history/', () => {
    return HttpResponse.json({
      exports: [
        {
          id: 1,
          export_type: 'participant_data',
          export_format: 'csv',
          status: 'completed',
          created_at: '2024-01-01T00:00:00Z',
        },
      ],
    });
  }),

  // Privacy endpoints
  http.post('*/api/research/privacy/anonymize/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({
      success: true,
      participant_id: body.participant_id,
      message: 'Participant anonymized successfully',
    });
  }),

  http.get('*/api/research/privacy/gdpr-status/', () => {
    return HttpResponse.json({
      overall_compliance: 95.0,
      studies: [
        {
          id: 1,
          name: 'Test Study',
          compliance_score: 95.0,
        },
      ],
    });
  }),

  // Utilities endpoints
  http.post('*/api/research/utils/generate-ids/', async ({ request }) => {
    const body = await request.json() as any;
    const count = body.count || 5;
    const prefix = body.prefix || 'P';
    return HttpResponse.json({
      count,
      participant_ids: Array.from({ length: count }, (_, i) => 
        `${prefix}${String(i + 1).padStart(3, '0')}`
      ),
    });
  }),

  http.post('*/api/research/utils/calculate-sample-size/', async ({ request }) => {
    const body = await request.json() as any;
    return HttpResponse.json({
      sample_size_per_group: 32,
      total_sample_size: 64,
      effect_size: body.effect_size,
      alpha: body.alpha,
      power: body.power,
    });
  }),

  http.get('*/api/research/utils/validate-integrity/', () => {
    return HttpResponse.json({
      checks_performed: 5,
      issues_found: 0,
      statistics: {
        total_participants: 10,
        total_interactions: 1500,
        total_exports: 5,
      },
    });
  }),

  // Dashboard endpoints
  http.get('*/api/dashboard/overview/', () => {
    return HttpResponse.json({
      total_studies: 3,
      total_participants: 25,
      completion_rate: 78.5,
      active_sessions: 5,
    });
  }),

  http.get('*/api/dashboard/activity/', () => {
    return HttpResponse.json({
      daily_registrations: [
        { date: '2024-01-01', count: 5 },
        { date: '2024-01-02', count: 3 },
        { date: '2024-01-03', count: 7 },
      ],
      daily_completions: [
        { date: '2024-01-01', count: 2 },
        { date: '2024-01-02', count: 1 },
        { date: '2024-01-03', count: 4 },
      ],
    });
  }),

  // Catch-all for unhandled requests
  http.all('*', ({ request }) => {
    console.warn(`Unhandled request: ${request.method} ${request.url}`);
    return HttpResponse.json({ error: 'Endpoint not found' }, { status: 404 });
  }),
];

// Create and export server
export const server = setupServer(...handlers);