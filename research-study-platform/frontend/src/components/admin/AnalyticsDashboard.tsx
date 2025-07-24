import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  UsersIcon, 
  ClockIcon, 
  ArrowTrendingUpIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  EyeIcon,
  QuestionMarkCircleIcon,
  CalendarDaysIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { BarChart, LineChart, PieChart, AreaChart } from '../charts';
import { researchApi } from '../../services/api';

interface StudyOverview {
  name: string;
  total_participants: number;
  active_participants: number;
  completed_participants: number;
  completion_rate: number;
  created_at: string;
}

interface ParticipantStats {
  total_participants: number;
  completed_participants: number;
  active_participants: number;
  withdrawn_participants: number;
  completion_rate: number;
  group_distribution: Record<string, number>;
  consent_completion_rate: number;
  pre_quiz_completion_rate: number;
  interaction_completion_rate: number;
  post_quiz_completion_rate: number;
  average_session_duration: number;
  average_interaction_duration: number;
}

interface InteractionStats {
  total_interactions: number;
  log_type_distribution: Record<string, number>;
  daily_activity: Array<{day: string; count: number}>;
}

interface ChatStats {
  total_messages: number;
  message_type_distribution: Record<string, number>;
  average_response_time_ms: number;
  total_tokens: number;
  total_cost_usd: number;
}

interface PDFStats {
  total_page_views: number;
  average_time_per_page: number;
  pdf_distribution: Record<string, number>;
  most_viewed_pages: Array<{
    pdf_name: string;
    page_number: number;
    total_time: number;
    view_count: number;
  }>;
}

interface QuizStats {
  total_responses: number;
  quiz_type_distribution: Record<string, number>;
  accuracy_rate: number;
  average_response_time_seconds: number;
}

interface TimelineData {
  daily_registrations: Array<{day: string; count: number}>;
  daily_completions: Array<{day: string; count: number}>;
}

interface AnalyticsData {
  study_overview: StudyOverview;
  participant_stats: ParticipantStats;
  interaction_stats: InteractionStats;
  chat_stats: ChatStats;
  pdf_stats: PDFStats;
  quiz_stats: QuizStats;
  timeline_data: TimelineData;
}

const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStudy, setSelectedStudy] = useState<string>('');
  const [studies, setStudies] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchStudies();
  }, []);

  useEffect(() => {
    if (selectedStudy) {
      fetchAnalytics(selectedStudy);
    }
  }, [selectedStudy]);

  const fetchStudies = async () => {
    try {
      const response = await researchApi.getStudies();
      setStudies(response.data);
      if (response.data.length > 0) {
        setSelectedStudy(response.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching studies:', err);
      setError('Failed to fetch studies');
    }
  };

  const fetchAnalytics = async (studyId: string) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔍 Fetching analytics for study:', studyId);
      const response = await researchApi.getStudyAnalytics(studyId);
      console.log('📊 Analytics response:', response.data);
      setAnalytics(response.data);
    } catch (err: any) {
      console.error('❌ Error fetching analytics:', err);
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
      }
      setError(`Failed to fetch analytics data: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const refreshAnalytics = async () => {
    if (selectedStudy) {
      setRefreshing(true);
      await fetchAnalytics(selectedStudy);
      setRefreshing(false);
    }
  };

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4,
      maximumFractionDigits: 4
    }).format(amount);
  };

  const prepareGroupDistributionData = (groupData: Record<string, number>) => {
    return Object.entries(groupData).map(([name, value]) => ({
      name,
      value
    }));
  };

  const prepareInteractionTypeData = (interactionData: Record<string, number>) => {
    return Object.entries(interactionData)
      .map(([name, value]) => ({
        name: name.replace('_', ' ').toUpperCase(),
        value
      }))
      .sort((a, b) => b.value - a.value);
  };

  const prepareCompletionProgressData = (participantStats: ParticipantStats) => {
    return [
      { phase: 'Consent', percentage: participantStats.consent_completion_rate },
      { phase: 'Pre-Quiz', percentage: participantStats.pre_quiz_completion_rate },
      { phase: 'Interaction', percentage: participantStats.interaction_completion_rate },
      { phase: 'Post-Quiz', percentage: participantStats.post_quiz_completion_rate }
    ];
  };

  const prepareTimelineData = (registrations: any[], completions: any[]) => {
    return registrations.map((reg, index) => ({
      day: reg.day.slice(5, 10),
      registrations: reg.count,
      completions: completions[index]?.count || 0
    }));
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            <span className="text-gray-600">Loading analytics...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={() => selectedStudy && fetchAnalytics(selectedStudy)}
            className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="text-gray-600 mb-4">
            {studies.length === 0 
              ? 'No research studies found. Please create a study first.' 
              : selectedStudy 
                ? 'No analytics data available for the selected study.'
                : 'Please select a study to view analytics.'}
          </div>
          {studies.length > 0 && !selectedStudy && (
            <div className="text-sm text-gray-500">
              Use the study selector in the top right to choose a study.
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">Comprehensive study analytics and insights</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedStudy}
            onChange={(e) => setSelectedStudy(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Select Study</option>
            {studies.map((study) => (
              <option key={study.id} value={study.id}>
                {study.name}
              </option>
            ))}
          </select>
          <button
            onClick={refreshAnalytics}
            disabled={refreshing}
            className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50"
          >
            <ArrowPathIcon className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Study Overview */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Study Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Participants</p>
                <p className="text-2xl font-bold">{analytics.study_overview.total_participants}</p>
              </div>
              <UsersIcon className="h-8 w-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Participants</p>
                <p className="text-2xl font-bold">{analytics.study_overview.active_participants}</p>
              </div>
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="text-2xl font-bold">{analytics.study_overview.completed_participants}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-purple-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completion Rate</p>
                <p className="text-2xl font-bold">{analytics.study_overview.completion_rate.toFixed(1)}%</p>
              </div>
              <ArrowTrendingUpIcon className="h-8 w-8 text-orange-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Participant Statistics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Participant Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium mb-3">Completion Progress</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Consent</span>
                <span className="text-sm font-medium">{analytics.participant_stats.consent_completion_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Pre-Quiz</span>
                <span className="text-sm font-medium">{analytics.participant_stats.pre_quiz_completion_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Interaction</span>
                <span className="text-sm font-medium">{analytics.participant_stats.interaction_completion_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Post-Quiz</span>
                <span className="text-sm font-medium">{analytics.participant_stats.post_quiz_completion_rate.toFixed(1)}%</span>
              </div>
            </div>
          </div>
          <div>
            <h3 className="font-medium mb-3">Group Distribution</h3>
            <div className="space-y-2">
              {Object.entries(analytics.participant_stats.group_distribution).map(([group, count]) => (
                <div key={group} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{group} Group</span>
                  <span className="text-sm font-medium">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <ClockIcon className="h-5 w-5 text-gray-500" />
              <span className="text-sm text-gray-600">Average Session Duration</span>
            </div>
            <p className="text-lg font-semibold mt-1">
              {formatDuration(analytics.participant_stats.average_session_duration)}
            </p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center space-x-2">
              <ClockIcon className="h-5 w-5 text-gray-500" />
              <span className="text-sm text-gray-600">Average Interaction Duration</span>
            </div>
            <p className="text-lg font-semibold mt-1">
              {formatDuration(analytics.participant_stats.average_interaction_duration)}
            </p>
          </div>
        </div>
      </div>

      {/* Interaction Statistics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Interaction Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <EyeIcon className="h-5 w-5 text-gray-500" />
              <span className="font-medium">Total Interactions</span>
            </div>
            <p className="text-2xl font-bold">{analytics.interaction_stats.total_interactions}</p>
          </div>
          <div>
            <h3 className="font-medium mb-3">Interaction Types</h3>
            <div className="space-y-1">
              {Object.entries(analytics.interaction_stats.log_type_distribution)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 5)
                .map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{type.replace('_', ' ')}</span>
                    <span className="text-sm font-medium">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>

      {/* Chat Statistics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Chat Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold">{analytics.chat_stats.total_messages}</p>
              </div>
              <ChatBubbleLeftRightIcon className="h-8 w-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold">{Math.round(analytics.chat_stats.average_response_time_ms)}ms</p>
              </div>
              <ClockIcon className="h-8 w-8 text-green-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Tokens</p>
                <p className="text-2xl font-bold">{analytics.chat_stats.total_tokens.toLocaleString()}</p>
              </div>
              <DocumentTextIcon className="h-8 w-8 text-purple-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Cost</p>
                <p className="text-2xl font-bold">{formatCurrency(analytics.chat_stats.total_cost_usd)}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-orange-500" />
            </div>
          </div>
        </div>
      </div>

      {/* PDF Statistics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">PDF Viewing Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="grid grid-cols-1 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <EyeIcon className="h-5 w-5 text-gray-500" />
                  <span className="text-sm text-gray-600">Total Page Views</span>
                </div>
                <p className="text-lg font-semibold mt-1">{analytics.pdf_stats.total_page_views}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center space-x-2">
                  <ClockIcon className="h-5 w-5 text-gray-500" />
                  <span className="text-sm text-gray-600">Avg Time per Page</span>
                </div>
                <p className="text-lg font-semibold mt-1">{Math.round(analytics.pdf_stats.average_time_per_page)}s</p>
              </div>
            </div>
          </div>
          <div>
            <h3 className="font-medium mb-3">Most Viewed Pages</h3>
            <div className="space-y-2">
              {analytics.pdf_stats.most_viewed_pages.slice(0, 5).map((page, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{page.pdf_name} - Page {page.page_number}</span>
                  <span className="text-sm font-medium">{Math.round(page.total_time)}s</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quiz Statistics */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Quiz Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Responses</p>
                <p className="text-2xl font-bold">{analytics.quiz_stats.total_responses}</p>
              </div>
              <QuestionMarkCircleIcon className="h-8 w-8 text-blue-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Accuracy Rate</p>
                <p className="text-2xl font-bold">{analytics.quiz_stats.accuracy_rate.toFixed(1)}%</p>
              </div>
              <ArrowTrendingUpIcon className="h-8 w-8 text-green-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Response Time</p>
                <p className="text-2xl font-bold">{Math.round(analytics.quiz_stats.average_response_time_seconds)}s</p>
              </div>
              <ClockIcon className="h-8 w-8 text-purple-500" />
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Quiz Types</p>
                <p className="text-2xl font-bold">{Object.keys(analytics.quiz_stats.quiz_type_distribution).length}</p>
              </div>
              <QuestionMarkCircleIcon className="h-8 w-8 text-orange-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Data */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Activity Timeline</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <CalendarDaysIcon className="h-5 w-5 text-gray-500" />
              <span className="font-medium">Daily Registrations</span>
            </div>
            <p className="text-lg font-semibold">
              {analytics.timeline_data.daily_registrations.reduce((sum, day) => sum + day.count, 0)} total
            </p>
          </div>
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <CalendarDaysIcon className="h-5 w-5 text-gray-500" />
              <span className="font-medium">Daily Completions</span>
            </div>
            <p className="text-lg font-semibold">
              {analytics.timeline_data.daily_completions.reduce((sum, day) => sum + day.count, 0)} total
            </p>
          </div>
        </div>
      </div>

      {/* Visual Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Group Distribution Chart */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <PieChart
            data={prepareGroupDistributionData(analytics.participant_stats.group_distribution)}
            title="Study Group Distribution"
            height={300}
            tooltipFormatter={(value: number, name: string) => [`${value} participants`, name]}
          />
        </div>

        {/* Completion Progress Chart */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <BarChart
            data={prepareCompletionProgressData(analytics.participant_stats)}
            xKey="phase"
            yKey="percentage"
            title="Completion Progress by Phase"
            color="#10B981"
            height={300}
            tooltipFormatter={(value: number) => [`${value.toFixed(1)}%`, 'Completion Rate']}
          />
        </div>
      </div>

      {/* Timeline Charts */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <LineChart
          data={prepareTimelineData(analytics.timeline_data.daily_registrations, analytics.timeline_data.daily_completions)}
          xKey="day"
          lines={[
            { key: 'registrations', color: '#3B82F6', name: 'Registrations' },
            { key: 'completions', color: '#10B981', name: 'Completions' }
          ]}
          title="Daily Activity Timeline"
          height={350}
          tooltipFormatter={(value: number, name: string) => [`${value} ${name.toLowerCase()}`, name]}
        />
      </div>

      {/* Interaction Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Interaction Types */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <BarChart
            data={prepareInteractionTypeData(analytics.interaction_stats.log_type_distribution)}
            xKey="name"
            yKey="value"
            title="User Interaction Types"
            color="#8B5CF6"
            height={300}
            tooltipFormatter={(value: number, name: string) => [`${value} interactions`, name]}
          />
        </div>

        {/* Daily Activity Area Chart */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <AreaChart
            data={analytics.interaction_stats.daily_activity.map(day => ({
              day: day.day.slice(5, 10),
              interactions: day.count
            }))}
            xKey="day"
            areas={[
              { key: 'interactions', color: '#F59E0B', name: 'Daily Interactions' }
            ]}
            title="Daily User Activity"
            height={300}
            tooltipFormatter={(value: number) => [`${value} interactions`, 'Daily Activity']}
          />
        </div>
      </div>

      {/* Research Comparison Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">ChatGPT vs Static Materials Comparison</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-800 mb-2">ChatGPT Group</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Participants</span>
                <span className="font-semibold">{analytics.participant_stats.group_distribution.CHATGPT}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg. Session Time</span>
                <span className="font-semibold">{formatDuration(analytics.participant_stats.average_interaction_duration)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Messages Sent</span>
                <span className="font-semibold">{analytics.chat_stats.total_messages}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-medium text-green-800 mb-2">PDF Group</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Participants</span>
                <span className="font-semibold">{analytics.participant_stats.group_distribution.PDF}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg. Session Time</span>
                <span className="font-semibold">{formatDuration(analytics.participant_stats.average_session_duration)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Pages Viewed</span>
                <span className="font-semibold">{analytics.pdf_stats.total_page_views}</span>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-medium text-purple-800 mb-2">Overall Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Completion Rate</span>
                <span className="font-semibold">{analytics.participant_stats.completion_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Quiz Accuracy</span>
                <span className="font-semibold">{analytics.quiz_stats.accuracy_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg. Response Time</span>
                <span className="font-semibold">{Math.round(analytics.quiz_stats.average_response_time_seconds)}s</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;