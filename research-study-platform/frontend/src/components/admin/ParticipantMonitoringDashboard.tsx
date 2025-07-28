import React, { useState, useEffect } from 'react';
import { researchApi } from '../../services/api';
import { BarChart, PieChart } from '../charts';
import toast from 'react-hot-toast';

interface Participant {
  id: string;
  username: string;
  email: string;
  participant_id: string;
  study_group: string;
  consent_completed: boolean;
  pre_quiz_completed: boolean;
  interaction_completed: boolean;
  post_quiz_completed: boolean;
  study_completed: boolean;
  completion_percentage: number;
  created_at: string;
}

interface ParticipantSummary {
  total_interactions: number;
  total_chat_messages: number;
  total_pdf_views: number;
  total_quiz_responses: number;
  session_duration: number;
  last_activity: string | null;
}

const ParticipantMonitoringDashboard: React.FC = () => {
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [filteredParticipants, setFilteredParticipants] = useState<Participant[]>([]);
  const [selectedParticipant, setSelectedParticipant] = useState<Participant | null>(null);
  const [participantSummary, setParticipantSummary] = useState<ParticipantSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  
  // Filters
  const [groupFilter, setGroupFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const fetchParticipants = async () => {
    try {
      setLoading(true);
      console.log('🔍 Loading participants for monitoring from database...');
      const response = await researchApi.getAllParticipants();
      setParticipants(response.data);
      setFilteredParticipants(response.data);
      console.log('✅ Successfully loaded participants for monitoring:', response.data.length, 'participants');
    } catch (error: any) {
      console.error('❌ Error fetching participants for monitoring:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Failed to load participants';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const fetchParticipantSummary = async (participantId: string) => {
    try {
      setSummaryLoading(true);
      // This would call the participant interaction summary endpoint
      // For now, we'll simulate the data structure
      const mockSummary: ParticipantSummary = {
        total_interactions: Math.floor(Math.random() * 100),
        total_chat_messages: Math.floor(Math.random() * 50),
        total_pdf_views: Math.floor(Math.random() * 200),
        total_quiz_responses: Math.floor(Math.random() * 20),
        session_duration: Math.floor(Math.random() * 3600),
        last_activity: new Date().toISOString()
      };
      setParticipantSummary(mockSummary);
    } catch (error: any) {
      console.error('❌ Error fetching participant summary:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      toast.error('Failed to load participant summary');
    } finally {
      setSummaryLoading(false);
    }
  };

  useEffect(() => {
    fetchParticipants();
  }, []);

  useEffect(() => {
    let filtered = participants;

    // Apply group filter
    if (groupFilter !== 'ALL') {
      filtered = filtered.filter(p => p.study_group === groupFilter);
    }

    // Apply status filter
    if (statusFilter !== 'ALL') {
      switch (statusFilter) {
        case 'COMPLETED':
          filtered = filtered.filter(p => p.study_completed);
          break;
        case 'IN_PROGRESS':
          filtered = filtered.filter(p => !p.study_completed && p.consent_completed);
          break;
        case 'NOT_STARTED':
          filtered = filtered.filter(p => !p.consent_completed);
          break;
      }
    }

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(p => 
        p.participant_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.username.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredParticipants(filtered);
  }, [participants, groupFilter, statusFilter, searchTerm]);

  const getStatusColor = (participant: Participant) => {
    if (participant.study_completed) return 'text-green-600 bg-green-100';
    if (participant.consent_completed) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getStatusText = (participant: Participant) => {
    if (participant.study_completed) return 'Completed';
    if (participant.post_quiz_completed) return 'Post-Quiz Done';
    if (participant.interaction_completed) return 'Learning Phase Done';
    if (participant.pre_quiz_completed) return 'Pre-Quiz Done';
    if (participant.consent_completed) return 'Consented';
    return 'Not Started';
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  // Calculate summary statistics
  const completionStats = {
    completed: filteredParticipants.filter(p => p.study_completed).length,
    inProgress: filteredParticipants.filter(p => !p.study_completed && p.consent_completed).length,
    notStarted: filteredParticipants.filter(p => !p.consent_completed).length,
  };

  const groupStats = {
    CHATGPT: filteredParticipants.filter(p => p.study_group === 'CHATGPT').length,
    PDF: filteredParticipants.filter(p => p.study_group === 'PDF').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Participant Monitoring</h1>
        <button
          onClick={fetchParticipants}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Total Participants</h3>
          <p className="text-2xl font-bold text-gray-900">{filteredParticipants.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">Completed</h3>
          <p className="text-2xl font-bold text-green-600">{completionStats.completed}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">In Progress</h3>
          <p className="text-2xl font-bold text-yellow-600">{completionStats.inProgress}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">ChatGPT Group</h3>
          <p className="text-2xl font-bold text-purple-600">{groupStats.CHATGPT}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500">PDF Group</h3>
          <p className="text-2xl font-bold text-orange-600">{groupStats.PDF}</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Progress Distribution</h2>
          <div className="h-64">
            <PieChart
              data={[
                { name: 'Completed', value: completionStats.completed },
                { name: 'In Progress', value: completionStats.inProgress },
                { name: 'Not Started', value: completionStats.notStarted }
              ]}
              title="Study Progress"
              colors={['#10B981', '#F59E0B', '#6B7280']}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Completion Funnel</h2>
          <div className="h-64">
            <BarChart
              data={[
                { 
                  category: 'Consent',
                  value: filteredParticipants.filter(p => p.consent_completed).length
                },
                { 
                  category: 'Pre-Quiz',
                  value: filteredParticipants.filter(p => p.pre_quiz_completed).length
                },
                { 
                  category: 'Learning',
                  value: filteredParticipants.filter(p => p.interaction_completed).length
                },
                { 
                  category: 'Post-Quiz',
                  value: filteredParticipants.filter(p => p.post_quiz_completed).length
                },
                { 
                  category: 'Completed',
                  value: filteredParticipants.filter(p => p.study_completed).length
                }
              ]}
              xKey="category"
              yKey="value"
              title="Phase Completion"
              color="#3B82F6"
            />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search participants..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          />
          
          <select
            value={groupFilter}
            onChange={(e) => setGroupFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Groups</option>
            <option value="CHATGPT">ChatGPT Group</option>
            <option value="PDF">PDF Group</option>
          </select>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="NOT_STARTED">Not Started</option>
          </select>
          
          <div className="text-sm text-gray-600 flex items-center">
            Showing {filteredParticipants.length} of {participants.length} participants
          </div>
        </div>
      </div>

      {/* Participants Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Participant
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Group
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredParticipants.map((participant) => (
                <tr key={participant.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {participant.participant_id}
                      </div>
                      <div className="text-sm text-gray-500">{participant.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      participant.study_group === 'CHATGPT' 
                        ? 'text-purple-800 bg-purple-100'
                        : 'text-orange-800 bg-orange-100'
                    }`}>
                      {participant.study_group}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(participant)}`}>
                      {getStatusText(participant)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${participant.completion_percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">
                        {participant.completion_percentage}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(participant.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => {
                        setSelectedParticipant(participant);
                        fetchParticipantSummary(participant.id);
                      }}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Participant Detail Modal */}
      {selectedParticipant && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-900">
                  Participant Details
                </h3>
                <button
                  onClick={() => {
                    setSelectedParticipant(null);
                    setParticipantSummary(null);
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-3">
                <div>
                  <strong>ID:</strong> {selectedParticipant.participant_id}
                </div>
                <div>
                  <strong>Email:</strong> {selectedParticipant.email}
                </div>
                <div>
                  <strong>Group:</strong> {selectedParticipant.study_group}
                </div>
                <div>
                  <strong>Progress:</strong> {selectedParticipant.completion_percentage}%
                </div>
                
                {summaryLoading ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                  </div>
                ) : participantSummary && (
                  <div className="border-t pt-3 mt-3">
                    <h4 className="font-bold mb-2">Activity Summary</h4>
                    <div className="space-y-2 text-sm">
                      <div>Interactions: {participantSummary.total_interactions}</div>
                      <div>Chat Messages: {participantSummary.total_chat_messages}</div>
                      <div>PDF Views: {participantSummary.total_pdf_views}</div>
                      <div>Quiz Responses: {participantSummary.total_quiz_responses}</div>
                      <div>Session Duration: {formatDuration(participantSummary.session_duration)}</div>
                      {participantSummary.last_activity && (
                        <div>Last Activity: {new Date(participantSummary.last_activity).toLocaleString()}</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ParticipantMonitoringDashboard;