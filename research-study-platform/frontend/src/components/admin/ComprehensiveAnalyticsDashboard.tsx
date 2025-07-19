import React, { useState, useEffect } from 'react';
import { BarChart, LineChart, PieChart, AreaChart } from '../charts';
import { researchApi } from '../../services/api';
import toast from 'react-hot-toast';

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

interface InteractionStats {
  total_interactions: number;
  log_type_distribution: Record<string, number>;
  daily_activity: Array<{
    day: string;
    count: number;
  }>;
}

interface TimelineData {
  daily_registrations: Array<{
    day: string;
    count: number;
  }>;
  daily_completions: Array<{
    day: string;
    count: number;
  }>;
}

interface StudyAnalytics {
  study_overview: StudyOverview;
  participant_stats: ParticipantStats;
  interaction_stats: InteractionStats;
  chat_stats: ChatStats;
  pdf_stats: PDFStats;
  quiz_stats: QuizStats;
  timeline_data: TimelineData;
}

interface DashboardOverview {
  total_studies: number;
  total_participants: number;
  active_participants: number;
  completed_participants: number;
  completion_rate: number;
  recent_registrations: number;
  recent_completions: number;
}

const ComprehensiveAnalyticsDashboard: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [studyAnalytics, setStudyAnalytics] = useState<StudyAnalytics | null>(null);
  const [activityTimeline, setActivityTimeline] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedStudyId, setSelectedStudyId] = useState<string>(''); // Will be set dynamically
  const [timeRange, setTimeRange] = useState<number>(30);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch overview data
      const overviewResponse = await researchApi.getDashboardOverview();
      setOverview(overviewResponse.data);

      // Fetch activity timeline
      const timelineResponse = await researchApi.getActivityTimeline(timeRange);
      setActivityTimeline(timelineResponse.data);

      // If no study is selected, try to get the first available study
      let studyIdToUse = selectedStudyId;
      if (!studyIdToUse) {
        try {
          const studiesResponse = await researchApi.getStudies();
          if (studiesResponse.data && studiesResponse.data.length > 0) {
            studyIdToUse = studiesResponse.data[0].id;
            setSelectedStudyId(studyIdToUse);
          }
        } catch (studiesError) {
          console.warn('Could not fetch studies:', studiesError);
        }
      }

      // Try to fetch detailed study analytics if a study ID is available
      if (studyIdToUse) {
        try {
          const analyticsResponse = await researchApi.getStudyAnalytics(studyIdToUse);
          setStudyAnalytics(analyticsResponse.data);
        } catch (analyticsError) {
          console.warn('Could not fetch study analytics:', analyticsError);
          // Continue without study analytics
        }
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [selectedStudyId, timeRange]);

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Research Analytics Dashboard</h1>
        <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="px-3 sm:px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={fetchDashboardData}
            className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h3 className="text-xs sm:text-sm font-medium text-gray-500">Total Participants</h3>
            <p className="text-xl sm:text-2xl font-bold text-gray-900">{overview.total_participants}</p>
            <p className="text-xs text-green-600">+{overview.recent_registrations} this week</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h3 className="text-xs sm:text-sm font-medium text-gray-500">Active Participants</h3>
            <p className="text-xl sm:text-2xl font-bold text-blue-600">{overview.active_participants}</p>
            <p className="text-xs text-gray-500">Currently enrolled</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h3 className="text-xs sm:text-sm font-medium text-gray-500">Completion Rate</h3>
            <p className="text-xl sm:text-2xl font-bold text-green-600">{overview.completion_rate.toFixed(1)}%</p>
            <p className="text-xs text-green-600">+{overview.recent_completions} completed this week</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h3 className="text-xs sm:text-sm font-medium text-gray-500">Active Studies</h3>
            <p className="text-xl sm:text-2xl font-bold text-purple-600">{overview.total_studies}</p>
            <p className="text-xs text-gray-500">Currently running</p>
          </div>
        </div>
      )}

      {/* Study Progress Funnel */}
      {studyAnalytics && studyAnalytics.participant_stats && (
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Study Progress Funnel</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="bg-blue-100 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-blue-800">Consent</h3>
                <p className="text-2xl font-bold text-blue-600">
                  {studyAnalytics.participant_stats.consent_completion_rate.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600">Completed consent form</p>
              </div>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-green-800">Pre-Quiz</h3>
                <p className="text-2xl font-bold text-green-600">
                  {studyAnalytics.participant_stats.pre_quiz_completion_rate.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600">Completed pre-assessment</p>
              </div>
            </div>
            
            <div className="text-center">
              <div className="bg-yellow-100 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-yellow-800">Interaction</h3>
                <p className="text-2xl font-bold text-yellow-600">
                  {studyAnalytics.participant_stats.interaction_completion_rate.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600">Completed learning phase</p>
              </div>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-purple-800">Post-Quiz</h3>
                <p className="text-2xl font-bold text-purple-600">
                  {studyAnalytics.participant_stats.post_quiz_completion_rate.toFixed(1)}%
                </p>
                <p className="text-sm text-gray-600">Completed post-assessment</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Activity Timeline */}
      {activityTimeline && (
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Participant Activity Timeline</h2>
          <div className="h-64 sm:h-80">
            <LineChart
              data={activityTimeline.daily_registrations.map((item, index) => ({
                date: item.day,
                registrations: item.count,
                completions: activityTimeline.daily_completions[index]?.count || 0
              }))}
              xKey="date"
              lines={[
                { key: 'registrations', name: 'New Registrations', color: '#3B82F6' },
                { key: 'completions', name: 'Study Completions', color: '#10B981' }
              ]}
              title="Daily Activity"
            />
          </div>
        </div>
      )}

      {/* Study Group Distribution and Performance Comparison */}
      {studyAnalytics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Study Group Distribution</h2>
            <div className="h-48 sm:h-64">
              <PieChart
                data={Object.entries(studyAnalytics.participant_stats.group_distribution).map(([group, count]) => ({
                  name: group,
                  value: count
                }))}
                title="Participants by Group"
                colors={['#8B5CF6', '#F59E0B']}
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Quiz Performance</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Overall Accuracy Rate</span>
                <span className="text-xl font-bold text-green-600">
                  {studyAnalytics.quiz_stats.accuracy_rate.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Average Response Time</span>
                <span className="text-xl font-bold text-blue-600">
                  {formatDuration(studyAnalytics.quiz_stats.average_response_time_seconds)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Responses</span>
                <span className="text-xl font-bold text-gray-900">
                  {studyAnalytics.quiz_stats.total_responses.toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Engagement Metrics */}
      {studyAnalytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Chat Interactions</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Messages</span>
                <span className="font-bold">{studyAnalytics.chat_stats.total_messages.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Response Time</span>
                <span className="font-bold">{(studyAnalytics.chat_stats.average_response_time_ms / 1000).toFixed(1)}s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Tokens</span>
                <span className="font-bold">{studyAnalytics.chat_stats.total_tokens.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Cost</span>
                <span className="font-bold text-red-600">{formatCurrency(studyAnalytics.chat_stats.total_cost_usd)}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">PDF Engagement</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Page Views</span>
                <span className="font-bold">{studyAnalytics.pdf_stats.total_page_views.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Time per Page</span>
                <span className="font-bold">{formatDuration(studyAnalytics.pdf_stats.average_time_per_page)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Documents Viewed</span>
                <span className="font-bold">{Object.keys(studyAnalytics.pdf_stats.pdf_distribution).length}</span>
              </div>
            </div>
            
            {studyAnalytics.pdf_stats.most_viewed_pages.length > 0 && (
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Most Viewed Pages</h3>
                <div className="space-y-1">
                  {studyAnalytics.pdf_stats.most_viewed_pages.slice(0, 3).map((page, index) => (
                    <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                      <span className="font-medium">{page.pdf_name}</span> - Page {page.page_number}
                      <br />
                      <span className="text-gray-600">{page.view_count} views, {formatDuration(page.total_time)} total</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Session Duration</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Session Duration</span>
                <span className="font-bold">{formatDuration(studyAnalytics.participant_stats.average_session_duration)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Interaction Time</span>
                <span className="font-bold">{formatDuration(studyAnalytics.participant_stats.average_interaction_duration)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Interactions</span>
                <span className="font-bold">{studyAnalytics.interaction_stats.total_interactions.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interaction Patterns */}
      {studyAnalytics && studyAnalytics.interaction_stats.daily_activity.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Daily Interaction Patterns</h2>
          <div className="h-64 sm:h-80">
            <AreaChart
              data={studyAnalytics.interaction_stats.daily_activity.map(item => ({
                date: item.day,
                interactions: item.count
              }))}
              xKey="date"
              areas={[{
                key: 'interactions',
                color: '#8B5CF6',
                name: 'Interactions'
              }]}
              title="Interactions per Day"
            />
          </div>
        </div>
      )}

      {/* Log Type Distribution */}
      {studyAnalytics && Object.keys(studyAnalytics.interaction_stats.log_type_distribution).length > 0 && (
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">Interaction Type Distribution</h2>
          <div className="h-64 sm:h-80">
            <BarChart
              data={Object.entries(studyAnalytics.interaction_stats.log_type_distribution).map(([type, count]) => ({
                category: type.replace('_', ' ').toUpperCase(),
                value: count
              }))}
              xKey="category"
              yKey="value"
              title="Interaction Types"
              color="#3B82F6"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ComprehensiveAnalyticsDashboard;