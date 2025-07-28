import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { 
  MagnifyingGlassIcon, 
  UserGroupIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { User } from '../../types';
import { researchApi } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import { getAnonymizedDisplayName, anonymizeEmail, getPartialHash } from '../../utils/privacy';

interface ParticipantStats {
  total: number;
  pdfGroup: number;
  chatgptGroup: number;
  completed: number;
  active: number;
}

const ParticipantManager: React.FC = () => {
  const [participants, setParticipants] = useState<User[]>([]);
  const [filteredParticipants, setFilteredParticipants] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterGroup, setFilterGroup] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedParticipant, setSelectedParticipant] = useState<User | null>(null);
  const [stats, setStats] = useState<ParticipantStats>({
    total: 0,
    pdfGroup: 0,
    chatgptGroup: 0,
    completed: 0,
    active: 0
  });

  useEffect(() => {
    loadParticipants();
  }, []);

  useEffect(() => {
    filterParticipants();
  }, [participants, searchTerm, filterGroup, filterStatus]);

  const loadParticipants = async () => {
    try {
      setIsLoading(true);
      console.log('🔍 Loading participants from database...');
      const response = await researchApi.getAllParticipants();
      const participantsData: User[] = response.data;
      
      setParticipants(participantsData);
      calculateStats(participantsData);
      console.log('✅ Successfully loaded participants from database:', participantsData.length, 'participants');
    } catch (error: any) {
      console.error('❌ Error loading participants:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Failed to load participants';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (participantList: User[]) => {
    const stats: ParticipantStats = {
      total: participantList.length,
      pdfGroup: participantList.filter(p => p.study_group === 'PDF').length,
      chatgptGroup: participantList.filter(p => p.study_group === 'CHATGPT').length,
      completed: participantList.filter(p => p.study_completed).length,
      active: participantList.filter(p => !p.study_completed && p.consent_completed).length
    };
    setStats(stats);
  };

  const filterParticipants = () => {
    let filtered = participants;

    // Search filter (now works with anonymized data)
    if (searchTerm) {
      filtered = filtered.filter(p =>
        getAnonymizedDisplayName(p).toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.participant_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        getPartialHash(p.id).toLowerCase().includes(searchTerm.toLowerCase()) ||
        getPartialHash(p.email).toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Group filter
    if (filterGroup !== 'all') {
      filtered = filtered.filter(p => p.study_group === filterGroup);
    }

    // Status filter
    if (filterStatus !== 'all') {
      switch (filterStatus) {
        case 'completed':
          filtered = filtered.filter(p => p.study_completed);
          break;
        case 'active':
          filtered = filtered.filter(p => !p.study_completed && p.consent_completed);
          break;
        case 'not_started':
          filtered = filtered.filter(p => !p.consent_completed);
          break;
      }
    }

    setFilteredParticipants(filtered);
  };


  const handleUpdateParticipant = async (participantId: string, updates: Partial<User>) => {
    try {
      setParticipants(prev => 
        prev.map(p => p.id === participantId ? { ...p, ...updates } : p)
      );
      console.log('✅ Participant updated successfully (mock operation)');
    } catch (error) {
      console.error('❌ Failed to update participant:', error);
    }
  };

  const handleDeleteParticipant = async (participantId: string) => {
    if (!window.confirm('Are you sure you want to delete this participant? This action cannot be undone.')) {
      return;
    }

    try {
      console.log('🗑️ Deleting participant from database:', participantId);
      
      // Call the API to delete from database
      await researchApi.deleteParticipant(participantId);
      
      // Update local state only after successful API call
      setParticipants(prev => prev.filter(p => p.id !== participantId));
      toast.success('Participant deleted successfully from database');
      console.log('✅ Participant deleted successfully from database');
    } catch (error: any) {
      console.error('❌ Error deleting participant:', error);
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response data:', error.response.data);
      }
      const errorMessage = error.response?.data?.error || error.response?.data?.detail || 'Failed to delete participant';
      toast.error(errorMessage);
    }
  };

  const getStatusBadge = (participant: User) => {
    if (participant.study_completed) {
      return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">Completed</span>;
    }
    if (participant.consent_completed) {
      return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Active</span>;
    }
    return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Not Started</span>;
  };

  const getGroupBadge = (group: string) => {
    const colors = {
      'PDF': 'bg-green-100 text-green-800',
      'CHATGPT': 'bg-blue-100 text-blue-800'
    };
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors[group as keyof typeof colors]}`}>
        {group}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
        <div className="bg-gray-50 p-3 sm:p-4 rounded-lg">
          <div className="flex items-center">
            <UserGroupIcon className="h-5 w-5 sm:h-6 sm:w-6 text-gray-600 mr-2" />
            <div>
              <div className="text-xl sm:text-2xl font-bold text-gray-900">{stats.total}</div>
              <div className="text-xs sm:text-sm text-gray-600">Total</div>
            </div>
          </div>
        </div>
        
        <div className="bg-green-50 p-3 sm:p-4 rounded-lg">
          <div className="flex items-center">
            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-green-500 rounded-full mr-2"></div>
            <div>
              <div className="text-xl sm:text-2xl font-bold text-green-900">{stats.pdfGroup}</div>
              <div className="text-xs sm:text-sm text-green-700">PDF Group</div>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 p-3 sm:p-4 rounded-lg">
          <div className="flex items-center">
            <div className="w-2 h-2 sm:w-3 sm:h-3 bg-blue-500 rounded-full mr-2"></div>
            <div>
              <div className="text-xl sm:text-2xl font-bold text-blue-900">{stats.chatgptGroup}</div>
              <div className="text-xs sm:text-sm text-blue-700">ChatGPT Group</div>
            </div>
          </div>
        </div>
        
        <div className="bg-yellow-50 p-3 sm:p-4 rounded-lg">
          <div className="flex items-center">
            <CheckCircleIcon className="h-5 w-5 sm:h-6 sm:w-6 text-yellow-600 mr-2" />
            <div>
              <div className="text-xl sm:text-2xl font-bold text-yellow-900">{stats.active}</div>
              <div className="text-xs sm:text-sm text-yellow-700">Active</div>
            </div>
          </div>
        </div>
        
        <div className="bg-purple-50 p-3 sm:p-4 rounded-lg">
          <div className="flex items-center">
            <CheckCircleIcon className="h-5 w-5 sm:h-6 sm:w-6 text-purple-600 mr-2" />
            <div>
              <div className="text-xl sm:text-2xl font-bold text-purple-900">{stats.completed}</div>
              <div className="text-xs sm:text-sm text-purple-700">Completed</div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col space-y-4 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
          <div className="relative flex-1 sm:flex-none">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
            <input
              type="text"
              placeholder="Search by participant ID or hash..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="flex space-x-2 sm:space-x-4">
            <select
              className="flex-1 sm:flex-none px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
              value={filterGroup}
              onChange={(e) => setFilterGroup(e.target.value)}
            >
              <option value="all">All Groups</option>
              <option value="PDF">PDF Group</option>
              <option value="CHATGPT">ChatGPT Group</option>
            </select>
            
            <select
              className="flex-1 sm:flex-none px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="active">Active</option>
              <option value="not_started">Not Started</option>
            </select>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
          <button
            onClick={loadParticipants}
            className="btn btn-outline flex items-center justify-center space-x-2 text-sm"
          >
            <ArrowPathIcon className="h-4 w-4" />
            <span>Refresh</span>
          </button>
          
          <div className="bg-blue-50 border border-blue-200 rounded-md px-3 sm:px-4 py-2">
            <p className="text-blue-800 text-xs sm:text-sm">
              <strong>Privacy:</strong> User identities are anonymized with hash identifiers to protect participant privacy. 
              <strong>Participants self-register</strong> at the main registration page.
            </p>
          </div>
        </div>
      </div>

      {/* Participants Table */}
      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Participant
              </th>
              <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Group
              </th>
              <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progress
              </th>
              <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="hidden sm:table-cell px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-3 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredParticipants.map((participant) => (
              <tr key={participant.id} className="hover:bg-gray-50">
                <td className="px-3 sm:px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {getAnonymizedDisplayName(participant)}
                    </div>
                    <div className="text-xs sm:text-sm text-gray-500">
                      <span className="block sm:inline">ID: {getPartialHash(participant.id)}</span>
                      <span className="hidden sm:inline"> • </span>
                      <span className="block sm:inline">Hash: {getPartialHash(participant.email)}</span>
                    </div>
                  </div>
                </td>
                <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                  {getGroupBadge(participant.study_group)}
                </td>
                <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5 sm:h-2 mr-2">
                      <div
                        className="bg-primary-600 h-1.5 sm:h-2 rounded-full"
                        style={{ width: `${participant.completion_percentage}%` }}
                      />
                    </div>
                    <span className="text-xs sm:text-sm text-gray-600 min-w-[40px]">
                      {participant.completion_percentage}%
                    </span>
                  </div>
                </td>
                <td className="px-3 sm:px-6 py-4 whitespace-nowrap">
                  {getStatusBadge(participant)}
                </td>
                <td className="hidden sm:table-cell px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(participant.created_at).toLocaleDateString()}
                </td>
                <td className="px-3 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-1 sm:space-x-2">
                    <button
                      onClick={() => setSelectedParticipant(participant)}
                      className="text-blue-600 hover:text-blue-900 p-1"
                      title="View Details"
                    >
                      <EyeIcon className="h-3 w-3 sm:h-4 sm:w-4" />
                    </button>
                    <button
                      onClick={() => {/* Handle edit */}}
                      className="text-green-600 hover:text-green-900 p-1"
                      title="Edit"
                    >
                      <PencilIcon className="h-3 w-3 sm:h-4 sm:w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteParticipant(participant.id)}
                      className="text-red-600 hover:text-red-900 p-1"
                      title="Delete"
                    >
                      <TrashIcon className="h-3 w-3 sm:h-4 sm:w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredParticipants.length === 0 && (
        <div className="text-center py-12">
          <UserGroupIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No participants found</h3>
          <p className="text-gray-500">
            {searchTerm || filterGroup !== 'all' || filterStatus !== 'all'
              ? 'Try adjusting your search or filter criteria.'
              : 'Get started by adding your first participant.'}
          </p>
        </div>
      )}


      {/* Participant Details Modal */}
      {selectedParticipant && (
        <ParticipantDetailsModal
          participant={selectedParticipant}
          onClose={() => setSelectedParticipant(null)}
          onUpdate={handleUpdateParticipant}
        />
      )}
    </div>
  );
};


// Participant Details Modal Component
const ParticipantDetailsModal: React.FC<{
  participant: User;
  onClose: () => void;
  onUpdate: (id: string, updates: Partial<User>) => void;
}> = ({ participant, onClose, onUpdate }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-4 sm:p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Participant Details: {getAnonymizedDisplayName(participant)}
        </h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Participant ID
            </label>
            <p className="text-sm text-gray-900">{participant.participant_id}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              User Hash
            </label>
            <p className="text-sm text-gray-900">{getPartialHash(participant.email)}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Study Group
            </label>
            <p className="text-sm text-gray-900">{participant.study_group}</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Progress
            </label>
            <p className="text-sm text-gray-900">{participant.completion_percentage}%</p>
          </div>
        </div>
        
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Study Progress</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Consent Form</span>
              {participant.consent_completed ? (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              ) : (
                <XCircleIcon className="h-4 w-4 text-red-500" />
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Pre-Assessment</span>
              {participant.pre_quiz_completed ? (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              ) : (
                <XCircleIcon className="h-4 w-4 text-red-500" />
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Learning Session</span>
              {participant.interaction_completed ? (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              ) : (
                <XCircleIcon className="h-4 w-4 text-red-500" />
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Post-Assessment</span>
              {participant.post_quiz_completed ? (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              ) : (
                <XCircleIcon className="h-4 w-4 text-red-500" />
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Study Complete</span>
              {participant.study_completed ? (
                <CheckCircleIcon className="h-4 w-4 text-green-500" />
              ) : (
                <XCircleIcon className="h-4 w-4 text-red-500" />
              )}
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="btn btn-outline"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ParticipantManager;