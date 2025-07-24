import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  UsersIcon, 
  ArrowTrendingUpIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  ChartPieIcon,
  BeakerIcon
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

const ResearchAnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStudy, setSelectedStudy] = useState<string>('');
  const [studies, setStudies] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

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
      
      console.log('🔬 Research: Fetching analytics for study:', studyId);
      const response = await researchApi.getStudyAnalytics(studyId);
      console.log('📈 Research: Analytics response:', response.data);
      setAnalytics(response.data);
    } catch (err: any) {
      console.error('❌ Research: Error fetching analytics:', err);
      if (err.response) {
        console.error('Response status:', err.response.status);
        console.error('Response data:', err.response.data);
      }
      setError(`Failed to fetch research analytics: ${err.response?.data?.detail || err.message}`);
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

  const handleExport = async (exportType: string) => {
    if (!selectedStudy) return;
    
    try {
      setExportLoading(true);
      let response;
      
      switch (exportType) {
        case 'all':
          response = await researchApi.exportAllData();
          break;
        case 'chat':
          response = await researchApi.exportChatInteractions();
          break;
        case 'pdf':
          response = await researchApi.exportPDFInteractions();
          break;
        case 'quiz':
          response = await researchApi.exportQuizResponses();
          break;
        case 'participants':
          response = await researchApi.exportParticipantData(selectedStudy, 'csv');
          break;
        default:
          return;
      }
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${exportType}_data_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting data:', err);
      setError('Failed to export data');
    } finally {
      setExportLoading(false);
    }
  };

  const prepareGroupDistributionData = (groupData: Record<string, number> | undefined) => {
    if (!groupData) return [];
    return Object.entries(groupData).map(([name, value]) => ({
      name,
      value
    }));
  };

  const prepareInteractionTypeData = (interactionData: Record<string, number> | undefined) => {
    if (!interactionData) return [];
    return Object.entries(interactionData)
      .map(([name, value]) => ({
        name: name.replace('_', ' ').toUpperCase(),
        value
      }))
      .sort((a, b) => b.value - a.value);
  };

  const prepareCompletionProgressData = (participantStats: ParticipantStats | undefined) => {
    if (!participantStats) return [];
    return [
      { phase: 'Consent', percentage: participantStats.consent_completion_rate || 0 },
      { phase: 'Pre-Quiz', percentage: participantStats.pre_quiz_completion_rate || 0 },
      { phase: 'Interaction', percentage: participantStats.interaction_completion_rate || 0 },
      { phase: 'Post-Quiz', percentage: participantStats.post_quiz_completion_rate || 0 }
    ];
  };

  const prepareTimelineData = (registrations: any[] | undefined, completions: any[] | undefined) => {
    if (!registrations || !completions) return [];
    
    const regMap = new Map(registrations.map(r => [r.day, r.count]));
    const compMap = new Map(completions.map(c => [c.day, c.count]));
    
    const allDays = Array.from(new Set([...registrations.map(r => r.day), ...completions.map(c => c.day)])).sort();
    
    return allDays.map(day => ({
      day: day.slice(5, 10),
      registrations: regMap.get(day) || 0,
      completions: compMap.get(day) || 0
    }));
  };

  const prepareComparisonData = (analytics: AnalyticsData | null) => {
    if (!analytics) return [];
    
    const chatGroupSize = analytics?.participant_stats?.group_distribution?.CHATGPT || 0;
    const pdfGroupSize = analytics?.participant_stats?.group_distribution?.PDF || 0;
    
    return [
      {
        metric: 'Participants',
        chatgpt: chatGroupSize,
        pdf: pdfGroupSize
      },
      {
        metric: 'Avg Session Time (min)',
        chatgpt: Math.round((analytics?.participant_stats?.average_interaction_duration || 0) / 60),
        pdf: Math.round((analytics?.participant_stats?.average_session_duration || 0) / 60)
      },
      {
        metric: 'Completion Rate (%)',
        chatgpt: analytics?.participant_stats?.completion_rate || 0,
        pdf: analytics?.participant_stats?.completion_rate || 0
      },
      {
        metric: 'Avg Response Time (s)',
        chatgpt: analytics?.quiz_stats?.average_response_time_seconds || 0,
        pdf: analytics?.quiz_stats?.average_response_time_seconds || 0
      }
    ];
  };


  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
            <span className="text-gray-600">Loading research analytics...</span>
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

  if (!analytics && !loading) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="text-gray-600 mb-4">
            {studies.length === 0 
              ? 'No research studies found. Please create a study first.' 
              : selectedStudy 
                ? 'No analytics data available for the selected study.'
                : 'Please select a study to view research analytics.'}
          </div>
          {studies.length > 0 && !selectedStudy && (
            <div className="text-sm text-gray-500">
              Use the study selector in the top right to choose a study.
            </div>
          )}
          {selectedStudy && (
            <button
              onClick={() => fetchAnalytics(selectedStudy)}
              className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 mt-4"
            >
              Retry Loading Data
            </button>
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
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <BeakerIcon className="h-8 w-8 mr-2 text-primary-600" />
            Research Analytics Dashboard
          </h1>
          <p className="text-gray-600">
            Comprehensive analytics for "Evaluating ChatGPT vs. Static Materials for Learning Basic Linux Commands"
          </p>
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

      {/* Study Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Participants</p>
              <p className="text-2xl font-bold text-blue-600">{analytics?.study_overview?.total_participants || 0}</p>
            </div>
            <UsersIcon className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Participants</p>
              <p className="text-2xl font-bold text-green-600">{analytics?.study_overview?.active_participants || 0}</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-purple-600">{analytics?.study_overview?.completed_participants || 0}</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-purple-500" />
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completion Rate</p>
              <p className="text-2xl font-bold text-orange-600">{analytics?.study_overview?.completion_rate?.toFixed(1) || 0}%</p>
            </div>
            <ChartPieIcon className="h-8 w-8 text-orange-500" />
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Group Distribution */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <PieChart
            data={prepareGroupDistributionData(analytics?.participant_stats?.group_distribution)}
            title="Study Group Distribution"
            height={300}
            tooltipFormatter={(value: number, name: string) => [`${value} participants`, name]}
          />
        </div>

        {/* Completion Progress */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <BarChart
            data={prepareCompletionProgressData(analytics?.participant_stats)}
            xKey="phase"
            yKey="percentage"
            title="Study Phase Completion Rates"
            color="#10B981"
            height={300}
            tooltipFormatter={(value: number) => [`${value.toFixed(1)}%`, 'Completion Rate']}
          />
        </div>
      </div>

      {/* Timeline and Activity */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <LineChart
          data={prepareTimelineData(analytics?.timeline_data?.daily_registrations, analytics?.timeline_data?.daily_completions)}
          xKey="day"
          lines={[
            { key: 'registrations', color: '#3B82F6', name: 'Daily Registrations' },
            { key: 'completions', color: '#10B981', name: 'Daily Completions' }
          ]}
          title="Study Activity Timeline"
          height={350}
          tooltipFormatter={(value: number, name: string) => [`${value} ${name.toLowerCase()}`, name]}
        />
      </div>

      {/* Interaction Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <BarChart
            data={prepareInteractionTypeData(analytics?.interaction_stats?.log_type_distribution)}
            xKey="name"
            yKey="value"
            title="User Interaction Types"
            color="#8B5CF6"
            height={300}
            tooltipFormatter={(value: number, name: string) => [`${value} interactions`, name]}
          />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <AreaChart
            data={analytics?.interaction_stats?.daily_activity?.map(day => ({
              day: day.day.slice(5, 10),
              interactions: day.count
            })) || []}
            xKey="day"
            areas={[
              { key: 'interactions', color: '#F59E0B', name: 'Daily Interactions' }
            ]}
            title="Daily Interaction Volume"
            height={300}
            tooltipFormatter={(value: number) => [`${value} interactions`, 'Activity']}
          />
        </div>
      </div>

      {/* Research Comparison Analysis */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">ChatGPT vs Static Materials Comparison</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-medium text-blue-800 mb-2">ChatGPT Group</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Participants</span>
                <span className="font-semibold">{analytics?.participant_stats?.group_distribution?.CHATGPT || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Messages</span>
                <span className="font-semibold">{analytics?.chat_stats?.total_messages || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg Response Time</span>
                <span className="font-semibold">{Math.round(analytics?.chat_stats?.average_response_time_ms || 0)}ms</span>
              </div>
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-medium text-green-800 mb-2">PDF Group</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Participants</span>
                <span className="font-semibold">{analytics?.participant_stats?.group_distribution?.PDF || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Page Views</span>
                <span className="font-semibold">{analytics?.pdf_stats?.total_page_views || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg Time/Page</span>
                <span className="font-semibold">{Math.round(analytics?.pdf_stats?.average_time_per_page || 0)}s</span>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-medium text-purple-800 mb-2">Overall Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Quiz Accuracy</span>
                <span className="font-semibold">{analytics?.quiz_stats?.accuracy_rate?.toFixed(1) || 0}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Responses</span>
                <span className="font-semibold">{analytics?.quiz_stats?.total_responses || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg Response Time</span>
                <span className="font-semibold">{Math.round(analytics?.quiz_stats?.average_response_time_seconds || 0)}s</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Comparison Chart */}
        <div className="mt-6">
          <BarChart
            data={prepareComparisonData(analytics)}
            xKey="metric"
            yKey="chatgpt"
            title="ChatGPT vs PDF Group Comparison"
            color="#3B82F6"
            height={300}
            tooltipFormatter={(value: number, name: string) => [`${value}`, name]}
          />
        </div>
      </div>

      {/* Export Section */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Data Export</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            onClick={() => handleExport('all')}
            disabled={exportLoading}
            className="flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Export All Data</span>
          </button>
          
          <button
            onClick={() => handleExport('participants')}
            disabled={exportLoading}
            className="flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-3 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Export Participants</span>
          </button>
          
          <button
            onClick={() => handleExport('chat')}
            disabled={exportLoading}
            className="flex items-center justify-center space-x-2 bg-purple-600 text-white px-4 py-3 rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Export Chat Data</span>
          </button>
          
          <button
            onClick={() => handleExport('pdf')}
            disabled={exportLoading}
            className="flex items-center justify-center space-x-2 bg-orange-600 text-white px-4 py-3 rounded-md hover:bg-orange-700 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Export PDF Data</span>
          </button>
          
          <button
            onClick={() => handleExport('quiz')}
            disabled={exportLoading}
            className="flex items-center justify-center space-x-2 bg-pink-600 text-white px-4 py-3 rounded-md hover:bg-pink-700 disabled:opacity-50"
          >
            <ArrowDownTrayIcon className="h-5 w-5" />
            <span>Export Quiz Data</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResearchAnalyticsDashboard;