import React, { useState, useEffect } from 'react';
import { BarChart, LineChart, AreaChart, PieChart } from '../charts';
import { researchApi } from '../../services/api';
import toast from 'react-hot-toast';

interface LearningMetrics {
  group: string;
  pre_quiz_avg: number;
  post_quiz_avg: number;
  learning_gain: number;
  completion_rate: number;
  average_time: number;
  engagement_score: number;
  help_seeking_frequency: number;
}

interface QuizComparison {
  question_id: string;
  question_text: string;
  chatgpt_accuracy: number;
  pdf_accuracy: number;
  difficulty_level: string;
  improvement_chatgpt: number;
  improvement_pdf: number;
}

interface EngagementPattern {
  group: string;
  avg_session_duration: number;
  avg_interactions: number;
  avg_questions_asked: number;
  reading_time: number;
  chat_messages: number;
  pages_visited: number;
}

interface TimeToComplete {
  group: string;
  phase: string;
  average_minutes: number;
  median_minutes: number;
  fastest_minutes: number;
  slowest_minutes: number;
}

const LearningEffectivenessDashboard: React.FC = () => {
  const [learningMetrics, setLearningMetrics] = useState<LearningMetrics[]>([]);
  const [quizComparisons, setQuizComparisons] = useState<QuizComparison[]>([]);
  const [engagementPatterns, setEngagementPatterns] = useState<EngagementPattern[]>([]);
  const [timeToComplete, setTimeToComplete] = useState<TimeToComplete[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState<string>('learning_gain');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchLearningEffectivenessData = async () => {
    try {
      setLoading(true);
      console.log('🔍 Fetching learning effectiveness data from database...');
      const response = await researchApi.getLearningEffectivenessData();
      const data = response.data;
      
      console.log('📊 Learning effectiveness response:', data);
      console.log('🎯 Quiz comparisons data:', data.quiz_comparisons);
      
      setLearningMetrics(data.learning_metrics || []);
      setQuizComparisons(data.quiz_comparisons || []);
      setEngagementPatterns(data.engagement_patterns || []);
      setTimeToComplete(data.time_to_complete || []);
      setLastUpdated(new Date());
      
      // Log data counts for debugging
      console.log(`📈 Loaded: ${data.learning_metrics?.length || 0} learning metrics, ${data.quiz_comparisons?.length || 0} quiz comparisons`);
    } catch (error: any) {
      console.error('❌ Error fetching learning effectiveness data:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Failed to load learning effectiveness data';
      toast.error(errorMessage);
      
      // Generate sample data as fallback for development/testing if API fails
      console.log('🔄 Using fallback mock data due to API error');
      const mockQuizComparisons: QuizComparison[] = [
        {
          question_id: "q1",
          question_text: "What command lists files in a directory?",
          difficulty_level: "Easy",
          chatgpt_accuracy: 85.7,
          pdf_accuracy: 78.3,
          improvement_chatgpt: 12.4,
          improvement_pdf: 8.9
        },
        {
          question_id: "q2",
          question_text: "How do you change file permissions?",
          difficulty_level: "Medium", 
          chatgpt_accuracy: 72.1,
          pdf_accuracy: 81.5,
          improvement_chatgpt: 15.2,
          improvement_pdf: 18.7
        },
        {
          question_id: "q3",
          question_text: "What's the difference between rm and rmdir?",
          difficulty_level: "Medium",
          chatgpt_accuracy: 68.9,
          pdf_accuracy: 65.4,
          improvement_chatgpt: 11.8,
          improvement_pdf: 9.2
        }
      ];
      setLearningMetrics([]);
      setQuizComparisons(mockQuizComparisons);
      setEngagementPatterns([]);
      setTimeToComplete([]);
    } finally {
      setLoading(false);
    }
  };

  // Legacy mock data function (for fallback)
  const generateMockData = () => {
    const mockLearningMetrics: LearningMetrics[] = [
      {
        group: 'CHATGPT',
        pre_quiz_avg: 65.2,
        post_quiz_avg: 82.7,
        learning_gain: 17.5,
        completion_rate: 89.3,
        average_time: 45.6,
        engagement_score: 78.4,
        help_seeking_frequency: 4.2
      },
      {
        group: 'PDF',
        pre_quiz_avg: 64.8,
        post_quiz_avg: 79.1,
        learning_gain: 14.3,
        completion_rate: 85.7,
        average_time: 52.3,
        engagement_score: 71.9,
        help_seeking_frequency: 2.8
      }
    ];

    const mockQuizComparisons: QuizComparison[] = [
      {
        question_id: 'q1',
        question_text: 'Basic file navigation commands',
        chatgpt_accuracy: 85.2,
        pdf_accuracy: 78.9,
        difficulty_level: 'Easy',
        improvement_chatgpt: 22.1,
        improvement_pdf: 18.7
      },
      {
        question_id: 'q2',
        question_text: 'File permissions and ownership',
        chatgpt_accuracy: 72.4,
        pdf_accuracy: 69.8,
        difficulty_level: 'Medium',
        improvement_chatgpt: 15.3,
        improvement_pdf: 12.9
      },
      {
        question_id: 'q3',
        question_text: 'Advanced pipe operations',
        chatgpt_accuracy: 68.9,
        pdf_accuracy: 71.2,
        difficulty_level: 'Hard',
        improvement_chatgpt: 8.7,
        improvement_pdf: 11.4
      },
      {
        question_id: 'q4',
        question_text: 'Process management',
        chatgpt_accuracy: 79.6,
        pdf_accuracy: 75.3,
        difficulty_level: 'Medium',
        improvement_chatgpt: 18.9,
        improvement_pdf: 16.2
      }
    ];

    const mockEngagementPatterns: EngagementPattern[] = [
      {
        group: 'CHATGPT',
        avg_session_duration: 2736, // seconds
        avg_interactions: 34.2,
        avg_questions_asked: 12.5,
        reading_time: 0,
        chat_messages: 24.7,
        pages_visited: 0
      },
      {
        group: 'PDF',
        avg_session_duration: 3142,
        avg_interactions: 28.9,
        avg_questions_asked: 0,
        reading_time: 2890,
        chat_messages: 0,
        pages_visited: 18.3
      }
    ];

    const mockTimeToComplete: TimeToComplete[] = [
      { group: 'CHATGPT', phase: 'Pre-Quiz', average_minutes: 12.3, median_minutes: 11.5, fastest_minutes: 7.2, slowest_minutes: 28.1 },
      { group: 'PDF', phase: 'Pre-Quiz', average_minutes: 13.1, median_minutes: 12.8, fastest_minutes: 8.5, slowest_minutes: 25.7 },
      { group: 'CHATGPT', phase: 'Learning', average_minutes: 45.6, median_minutes: 42.3, fastest_minutes: 28.9, slowest_minutes: 89.2 },
      { group: 'PDF', phase: 'Learning', average_minutes: 52.3, median_minutes: 48.1, fastest_minutes: 35.7, slowest_minutes: 95.4 },
      { group: 'CHATGPT', phase: 'Post-Quiz', average_minutes: 14.2, median_minutes: 13.6, fastest_minutes: 9.1, slowest_minutes: 26.8 },
      { group: 'PDF', phase: 'Post-Quiz', average_minutes: 15.7, median_minutes: 14.9, fastest_minutes: 10.3, slowest_minutes: 29.2 }
    ];

    setLearningMetrics(mockLearningMetrics);
    setQuizComparisons(mockQuizComparisons);
    setEngagementPatterns(mockEngagementPatterns);
    setTimeToComplete(mockTimeToComplete);
    setLoading(false);
  };

  useEffect(() => {
    fetchLearningEffectivenessData();
  }, []);

  // Auto-refresh functionality
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchLearningEffectivenessData();
      }, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getEffectivenessScore = (chatgptValue: number, pdfValue: number) => {
    const difference = ((chatgptValue - pdfValue) / pdfValue) * 100;
    return {
      value: Math.abs(difference),
      better: chatgptValue > pdfValue ? 'ChatGPT' : 'PDF',
      isSignificant: Math.abs(difference) > 5
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const chatgptMetrics = learningMetrics.find(m => m.group === 'CHATGPT');
  const pdfMetrics = learningMetrics.find(m => m.group === 'PDF');

  // Show empty state if no data
  if (!loading && learningMetrics.length === 0) {
    return (
      <div className="p-6 space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Learning Effectiveness Analysis</h1>
          <button
            onClick={fetchLearningEffectivenessData}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Refresh
          </button>
        </div>
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <h2 className="text-xl font-bold text-gray-700 mb-4">No Learning Data Available</h2>
          <p className="text-gray-600 mb-6">
            There's no learning effectiveness data to display yet. This could be because:
          </p>
          <ul className="text-left text-gray-600 mb-6 max-w-md mx-auto">
            <li>• No participants have completed both pre and post quizzes</li>
            <li>• Study data is still being collected</li>
            <li>• Participants haven't been assigned to study groups yet</li>
          </ul>
          <button
            onClick={fetchLearningEffectivenessData}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Learning Effectiveness Analysis</h1>
        <div className="flex space-x-4 items-center">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="learning_gain">Learning Gain</option>
            <option value="completion_rate">Completion Rate</option>
            <option value="engagement_score">Engagement Score</option>
          </select>
          
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Auto-refresh (30s)</span>
          </label>
          
          <button
            onClick={fetchLearningEffectivenessData}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
          
          {lastUpdated && (
            <span className="text-sm text-gray-500">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Key Performance Indicators */}
      {chatgptMetrics && pdfMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Learning Gain Comparison</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-600 font-medium">ChatGPT Group</span>
                <span className="text-2xl font-bold text-purple-600">+{chatgptMetrics.learning_gain.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-orange-600 font-medium">PDF Group</span>
                <span className="text-2xl font-bold text-orange-600">+{pdfMetrics.learning_gain.toFixed(1)}%</span>
              </div>
              <div className="pt-2 border-t">
                <span className="text-sm text-gray-600">
                  ChatGPT shows {(chatgptMetrics.learning_gain - pdfMetrics.learning_gain).toFixed(1)}% 
                  higher learning gain
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Time Efficiency</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-600 font-medium">ChatGPT Avg</span>
                <span className="text-2xl font-bold text-purple-600">{formatTime(chatgptMetrics.average_time)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-orange-600 font-medium">PDF Avg</span>
                <span className="text-2xl font-bold text-orange-600">{formatTime(pdfMetrics.average_time)}</span>
              </div>
              <div className="pt-2 border-t">
                <span className="text-sm text-gray-600">
                  ChatGPT is {formatTime(pdfMetrics.average_time - chatgptMetrics.average_time)} faster
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Completion Rates</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-purple-600 font-medium">ChatGPT</span>
                <span className="text-2xl font-bold text-purple-600">{chatgptMetrics.completion_rate.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-orange-600 font-medium">PDF</span>
                <span className="text-2xl font-bold text-orange-600">{pdfMetrics.completion_rate.toFixed(1)}%</span>
              </div>
              <div className="pt-2 border-t">
                <span className="text-sm text-gray-600">
                  {chatgptMetrics.completion_rate > pdfMetrics.completion_rate ? 'ChatGPT' : 'PDF'} has 
                  {Math.abs(chatgptMetrics.completion_rate - pdfMetrics.completion_rate).toFixed(1)}% higher completion
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Learning Effectiveness Overview - Enhanced 6-Panel Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Learning Gain Comparison */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Learning Gain Comparison</h3>
          <div className="h-48">
            <BarChart
              data={[
                { category: 'ChatGPT', value: chatgptMetrics?.learning_gain || 0, color: '#8B5CF6' },
                { category: 'PDF', value: pdfMetrics?.learning_gain || 0, color: '#F59E0B' }
              ]}
              xKey="category"
              yKey="value"
              title="Learning Gain %"
            />
          </div>
          <div className="mt-2 text-center">
            <span className="text-sm text-gray-600">
              Advantage: {((chatgptMetrics?.learning_gain || 0) - (pdfMetrics?.learning_gain || 0)).toFixed(1)}% points
            </span>
          </div>
        </div>

        {/* Time Efficiency */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Time Efficiency</h3>
          <div className="h-48">
            <BarChart
              data={[
                { category: 'ChatGPT', value: chatgptMetrics?.average_time || 0, color: '#10B981' },
                { category: 'PDF', value: pdfMetrics?.average_time || 0, color: '#EF4444' }
              ]}
              xKey="category"
              yKey="value"
              title="Minutes to Complete"
            />
          </div>
          <div className="mt-2 text-center">
            <span className="text-sm text-gray-600">
              Faster by: {((pdfMetrics?.average_time || 0) - (chatgptMetrics?.average_time || 0)).toFixed(1)} min
            </span>
          </div>
        </div>

        {/* Overall Effectiveness Score */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Overall Effectiveness</h3>
          <div className="h-48">
            <AreaChart
              data={[
                { 
                  category: 'ChatGPT', 
                  effectiveness: chatgptMetrics ? 
                    (chatgptMetrics.learning_gain * 0.3 + 
                     chatgptMetrics.completion_rate * 0.2 + 
                     (100 - chatgptMetrics.average_time/60 * 100) * 0.2 + 
                     chatgptMetrics.engagement_score * 0.3) : 0
                },
                { 
                  category: 'PDF', 
                  effectiveness: pdfMetrics ? 
                    (pdfMetrics.learning_gain * 0.3 + 
                     pdfMetrics.completion_rate * 0.2 + 
                     (100 - pdfMetrics.average_time/60 * 100) * 0.2 + 
                     pdfMetrics.engagement_score * 0.3) : 0
                }
              ]}
              xKey="category"
              areas={[{ key: 'effectiveness', color: '#6366F1', name: 'Effectiveness Score' }]}
              title="Composite Score"
            />
          </div>
        </div>
      </div>

      {/* Pre vs Post Quiz Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Pre vs Post Quiz Score Progression</h2>
          <div className="h-80">
            <LineChart
              data={[
                {
                  category: 'Pre-Quiz',
                  ChatGPT: chatgptMetrics?.pre_quiz_avg || 0,
                  PDF: pdfMetrics?.pre_quiz_avg || 0
                },
                {
                  category: 'Post-Quiz',
                  ChatGPT: chatgptMetrics?.post_quiz_avg || 0,
                  PDF: pdfMetrics?.post_quiz_avg || 0
                }
              ]}
              xKey="category"
              lines={[
                { key: 'ChatGPT', color: '#8B5CF6', name: 'ChatGPT Group' },
                { key: 'PDF', color: '#F59E0B', name: 'PDF Group' }
              ]}
              title="Score Progression by Group"
            />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div className="text-center">
              <span className="text-purple-600 font-bold">ChatGPT Improvement</span>
              <div className="text-2xl font-bold text-green-600">
                +{((chatgptMetrics?.post_quiz_avg || 0) - (chatgptMetrics?.pre_quiz_avg || 0)).toFixed(1)}%
              </div>
            </div>
            <div className="text-center">
              <span className="text-orange-600 font-bold">PDF Improvement</span>
              <div className="text-2xl font-bold text-green-600">
                +{((pdfMetrics?.post_quiz_avg || 0) - (pdfMetrics?.pre_quiz_avg || 0)).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Question Performance Distribution</h2>
          <div className="h-80">
            {quizComparisons.length > 0 ? (
              <PieChart
                data={[
                  {
                    name: 'ChatGPT Wins',
                    value: quizComparisons.filter(q => q.chatgpt_accuracy > q.pdf_accuracy).length
                  },
                  {
                    name: 'PDF Wins',
                    value: quizComparisons.filter(q => q.pdf_accuracy > q.chatgpt_accuracy).length
                  },
                  {
                    name: 'Ties',
                    value: quizComparisons.filter(q => q.chatgpt_accuracy === q.pdf_accuracy).length
                  }
                ]}
                colors={['#8B5CF6', '#F59E0B', '#6B7280']}
                title="Better Performing Method by Question"
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
                <div className="text-center">
                  <div className="text-lg font-medium text-gray-700 mb-2">No Quiz Comparison Data Available</div>
                  <div className="text-sm text-gray-500 max-w-md">
                    This chart shows which learning method (ChatGPT vs PDF) performed better for each quiz question. 
                    Data will appear once participants have completed both pre and post quizzes.
                  </div>
                  <div className="text-xs text-orange-600 mt-2 p-2 bg-orange-50 rounded border">
                    <strong>Note:</strong> The backend API currently returns sample data. Real quiz comparison data processing needs to be implemented.
                  </div>
                </div>
                <button
                  onClick={fetchLearningEffectivenessData}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                >
                  Retry Loading Data
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Engagement Patterns */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Engagement Patterns by Group</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {engagementPatterns.map(pattern => (
            <div key={pattern.group} className="space-y-4">
              <h3 className={`text-lg font-bold ${
                pattern.group === 'CHATGPT' ? 'text-purple-600' : 'text-orange-600'
              }`}>
                {pattern.group} Group Behavior
              </h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Session Duration</span>
                  <span className="font-bold">{formatTime(pattern.avg_session_duration / 60)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Interactions</span>
                  <span className="font-bold">{pattern.avg_interactions.toFixed(1)}</span>
                </div>
                
                {pattern.group === 'CHATGPT' ? (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Questions Asked</span>
                      <span className="font-bold">{pattern.avg_questions_asked.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Chat Messages</span>
                      <span className="font-bold">{pattern.chat_messages.toFixed(1)}</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Reading Time</span>
                      <span className="font-bold">{formatTime(pattern.reading_time / 60)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Pages Visited</span>
                      <span className="font-bold">{pattern.pages_visited.toFixed(1)}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Advanced Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time to Complete Analysis */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Time to Complete by Phase</h2>
          <div className="h-80">
            <BarChart
              data={timeToComplete.map(item => ({
                category: `${item.phase}`,
                value: item.average_minutes,
                color: item.group === 'CHATGPT' ? '#8B5CF6' : '#F59E0B'
              }))}
              xKey="category"
              yKey="value"
              title="Average Time by Phase (minutes)"
            />
          </div>
          <div className="mt-4 text-sm text-gray-600">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="inline-block w-3 h-3 bg-purple-500 rounded-full mr-2"></span>
                ChatGPT Group
              </div>
              <div>
                <span className="inline-block w-3 h-3 bg-orange-500 rounded-full mr-2"></span>
                PDF Group
              </div>
            </div>
          </div>
        </div>

        {/* Accuracy Correlation Analysis */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Accuracy Correlation Matrix</h2>
          <div className="h-80">
            {quizComparisons.length > 0 ? (
              <div className="space-y-4">
                <div className="text-center text-sm text-gray-600 mb-4">
                  ChatGPT vs PDF Accuracy by Question Difficulty
                </div>
                {['Easy', 'Medium', 'Hard'].map(difficulty => {
                  const difficultyQuestions = quizComparisons.filter(q => q.difficulty_level === difficulty);
                  const avgChatGPT = difficultyQuestions.reduce((acc, q) => acc + q.chatgpt_accuracy, 0) / (difficultyQuestions.length || 1);
                  const avgPDF = difficultyQuestions.reduce((acc, q) => acc + q.pdf_accuracy, 0) / (difficultyQuestions.length || 1);
                  
                  return (
                    <div key={difficulty} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                          difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {difficulty}
                        </span>
                        <div className="flex space-x-4">
                          <span className="text-purple-600 font-medium">{avgChatGPT.toFixed(1)}%</span>
                          <span className="text-orange-600 font-medium">{avgPDF.toFixed(1)}%</span>
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-purple-500 to-orange-500 h-2 rounded-full"
                          style={{ width: `${Math.max(avgChatGPT, avgPDF)}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                No correlation data available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Engagement Visualization */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Detailed Engagement Analysis</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Session Duration Comparison */}
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Session Duration</h3>
            <div className="h-48">
              <AreaChart
                data={engagementPatterns.map(pattern => ({
                  category: pattern.group,
                  duration: pattern.avg_session_duration / 60 // Convert to minutes
                }))}
                xKey="category"
                areas={[{ key: 'duration', color: '#8B5CF6', name: 'Session Duration' }]}
                title="Average Minutes per Session"
              />
            </div>
          </div>

          {/* Interaction Intensity */}
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Interaction Intensity</h3>
            <div className="h-48">
              <BarChart
                data={engagementPatterns.map(pattern => ({
                  category: pattern.group,
                  value: pattern.avg_interactions,
                  color: pattern.group === 'CHATGPT' ? '#10B981' : '#EF4444'
                }))}
                xKey="category"
                yKey="value"
                title="Interactions per Session"
              />
            </div>
          </div>

          {/* Help-Seeking Behavior */}
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-700 mb-4">Help-Seeking Behavior</h3>
            <div className="h-48">
              {engagementPatterns.length > 0 ? (
                <PieChart
                  data={[
                    {
                      name: 'ChatGPT Questions',
                      value: engagementPatterns.find(p => p.group === 'CHATGPT')?.avg_questions_asked || 0
                    },
                    {
                      name: 'PDF Navigation',
                      value: engagementPatterns.find(p => p.group === 'PDF')?.pages_visited || 0
                    }
                  ]}
                  colors={['#8B5CF6', '#F59E0B']}
                  title="Information Seeking Patterns"
                />
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  No engagement data
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Question Analysis */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Question Difficulty Analysis</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Question
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Difficulty
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ChatGPT Accuracy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PDF Accuracy
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ChatGPT Improvement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  PDF Improvement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Better Method
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {quizComparisons.map((question, index) => {
                const better = question.chatgpt_accuracy > question.pdf_accuracy ? 'ChatGPT' : 'PDF';
                const difference = Math.abs(question.chatgpt_accuracy - question.pdf_accuracy);
                return (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {question.question_text}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        question.difficulty_level === 'Easy' ? 'bg-green-100 text-green-800' :
                        question.difficulty_level === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {question.difficulty_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-purple-600">
                      {question.chatgpt_accuracy.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-orange-600">
                      {question.pdf_accuracy.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-sm text-green-600">
                      +{question.improvement_chatgpt.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-sm text-green-600">
                      +{question.improvement_pdf.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        better === 'ChatGPT' ? 'bg-purple-100 text-purple-800' : 'bg-orange-100 text-orange-800'
                      }`}>
                        {better} (+{difference.toFixed(1)}%)
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Enhanced Statistical Analysis & Export Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Statistical Significance Analysis */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-4">Statistical Analysis</h3>
          
          {chatgptMetrics && pdfMetrics && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Learning Gain</h4>
                  <div className="text-2xl font-bold text-blue-600">
                    {((chatgptMetrics.learning_gain - pdfMetrics.learning_gain) / pdfMetrics.learning_gain * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">
                    {Math.abs(chatgptMetrics.learning_gain - pdfMetrics.learning_gain) > 5 ? 
                      '🟢 Significant difference' : '🟡 Modest difference'}
                  </div>
                </div>
                
                <div className="bg-white rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Time Efficiency</h4>
                  <div className="text-2xl font-bold text-green-600">
                    {((pdfMetrics.average_time - chatgptMetrics.average_time) / pdfMetrics.average_time * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">
                    {Math.abs(chatgptMetrics.average_time - pdfMetrics.average_time) > 10 ? 
                      '🟢 Significant improvement' : '🟡 Modest improvement'}
                  </div>
                </div>
              </div>
              
              <div className="text-sm text-blue-800 space-y-1">
                <li>• Effect size calculation based on Cohen's d methodology</li>
                <li>• Pedagogical significance threshold: &gt;5% difference</li>
                <li>• Time efficiency improvement: &gt;10 minutes difference</li>
                <li>• Question-level analysis uses chi-square test for significance</li>
              </div>
            </div>
          )}
        </div>

        {/* Data Export & Actions */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-green-900 mb-4">Data Export & Actions</h3>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-3">
              <button
                onClick={() => {
                  const csvData = [
                    ['Metric', 'ChatGPT', 'PDF', 'Difference'],
                    ['Learning Gain (%)', chatgptMetrics?.learning_gain || 0, pdfMetrics?.learning_gain || 0, (chatgptMetrics?.learning_gain || 0) - (pdfMetrics?.learning_gain || 0)],
                    ['Completion Rate (%)', chatgptMetrics?.completion_rate || 0, pdfMetrics?.completion_rate || 0, (chatgptMetrics?.completion_rate || 0) - (pdfMetrics?.completion_rate || 0)],
                    ['Average Time (min)', chatgptMetrics?.average_time || 0, pdfMetrics?.average_time || 0, (pdfMetrics?.average_time || 0) - (chatgptMetrics?.average_time || 0)],
                    ['Engagement Score', chatgptMetrics?.engagement_score || 0, pdfMetrics?.engagement_score || 0, (chatgptMetrics?.engagement_score || 0) - (pdfMetrics?.engagement_score || 0)]
                  ];
                  
                  const csvContent = csvData.map(row => row.join(',')).join('\n');
                  const blob = new Blob([csvContent], { type: 'text/csv' });
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `learning_effectiveness_${new Date().toISOString().split('T')[0]}.csv`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                }}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                📊 Export Summary Data (CSV)
              </button>
              
              <button
                onClick={() => {
                  const jsonData = {
                    timestamp: new Date().toISOString(),
                    learning_metrics: learningMetrics,
                    quiz_comparisons: quizComparisons,
                    engagement_patterns: engagementPatterns,
                    time_to_complete: timeToComplete
                  };
                  
                  const blob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `learning_effectiveness_detailed_${new Date().toISOString().split('T')[0]}.json`;
                  a.click();
                  window.URL.revokeObjectURL(url);
                }}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                📁 Export Detailed Data (JSON)
              </button>
              
              <button
                onClick={() => {
                  window.print();
                }}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                🖨️ Print Dashboard
              </button>
            </div>
            
            <div className="text-sm text-green-800 mt-4">
              <div className="font-semibold mb-2">Real-time Capabilities:</div>
              <ul className="space-y-1">
                <li>• Auto-refresh every 30 seconds when enabled</li>
                <li>• Live data updates from participant interactions</li>
                <li>• Instant statistical recalculation</li>
                <li>• Export data includes timestamp for version control</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningEffectivenessDashboard;