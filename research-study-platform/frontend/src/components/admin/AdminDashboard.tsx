import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  UsersIcon, 
  ChartBarIcon, 
  EyeIcon,
  ClipboardDocumentListIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';
import ParticipantManager from './ParticipantManager';
import ParticipantMonitoringDashboard from './ParticipantMonitoringDashboard';
import LearningEffectivenessDashboard from './LearningEffectivenessDashboard';
import ResearchDataVisualization from '../research/ResearchDataVisualization';

type AdminTab = 'participants' | 'monitoring' | 'effectiveness' | 'visualization';

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<AdminTab>('effectiveness');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is admin/researcher
    if (!user || (!user.is_staff && !user.is_superuser)) {
      navigate('/dashboard');
      return;
    }
    setIsLoading(false);
  }, [user, navigate]);

  const tabs = [
    {
      id: 'participants' as AdminTab,
      name: 'Participants',
      icon: UsersIcon,
      description: 'Manage participants and group assignments'
    },
    {
      id: 'monitoring' as AdminTab,
      name: 'Monitoring',
      icon: EyeIcon,
      description: 'Real-time participant monitoring and progress tracking'
    },
    {
      id: 'effectiveness' as AdminTab,
      name: 'Learning Analysis',
      icon: BeakerIcon,
      description: 'Learning effectiveness comparison between ChatGPT and PDF groups'
    },
    {
      id: 'visualization' as AdminTab,
      name: 'Data Visualization',
      icon: ChartBarIcon,
      description: 'Interactive research data visualization dashboard'
    },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'participants':
        return <ParticipantManager />;
      case 'monitoring':
        return <ParticipantMonitoringDashboard />;
      case 'effectiveness':
        return <LearningEffectivenessDashboard />;
      case 'visualization':
        return <ResearchDataVisualization />;
      default:
        return <LearningEffectivenessDashboard />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Research Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Linux Learning Study - Administrative Interface
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <ClipboardDocumentListIcon className="h-5 w-5 text-gray-500" />
              <span className="text-sm text-gray-600">
                Logged in as: {user?.username} (Researcher)
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <Icon className="h-5 w-5" />
                      <span>{tab.name}</span>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>
          
          {/* Tab Description */}
          <div className="px-6 py-3 bg-gray-50">
            <p className="text-sm text-gray-600">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-lg">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;