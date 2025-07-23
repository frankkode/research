import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  UsersIcon, 
  ChartBarIcon, 
  DocumentArrowDownIcon,
  CogIcon,
  EyeIcon,
  ShieldCheckIcon,
  ClipboardDocumentListIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';
import ParticipantManager from './ParticipantManager';
import AnalyticsDashboard from './AnalyticsDashboard';
import ResearchAnalyticsDashboard from './ResearchAnalyticsDashboard';
import ComprehensiveAnalyticsDashboard from './ComprehensiveAnalyticsDashboard';
import ParticipantMonitoringDashboard from './ParticipantMonitoringDashboard';
import LearningEffectivenessDashboard from './LearningEffectivenessDashboard';
import DataDebugger from './DataDebugger';
import ResearchDataVisualization from '../research/ResearchDataVisualization';
import TestDataVisualization from '../research/TestDataVisualization';

type AdminTab = 'participants' | 'monitoring' | 'analytics' | 'research' | 'effectiveness' | 'comprehensive' | 'visualization' | 'test' | 'export' | 'privacy' | 'utilities' | 'debug';

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<AdminTab>('comprehensive');
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
      id: 'comprehensive' as AdminTab,
      name: 'Overview',
      icon: ChartBarIcon,
      description: 'Comprehensive research analytics dashboard with all key metrics'
    },
    {
      id: 'effectiveness' as AdminTab,
      name: 'Learning Analysis',
      icon: BeakerIcon,
      description: 'Learning effectiveness comparison between ChatGPT and PDF groups'
    },
    {
      id: 'analytics' as AdminTab,
      name: 'Basic Analytics',
      icon: ChartBarIcon,
      description: 'View basic study statistics and performance'
    },
    {
      id: 'research' as AdminTab,
      name: 'Research Data',
      icon: BeakerIcon,
      description: 'Original research analytics with detailed charts'
    },
    {
      id: 'visualization' as AdminTab,
      name: 'Data Visualization',
      icon: ChartBarIcon,
      description: 'Interactive research data visualization dashboard'
    },
    {
      id: 'test' as AdminTab,
      name: 'Test Charts',
      icon: ChartBarIcon,
      description: 'Test visualization components with sample data'
    },
    {
      id: 'export' as AdminTab,
      name: 'Data Export',
      icon: DocumentArrowDownIcon,
      description: 'Export data for analysis'
    },
    {
      id: 'privacy' as AdminTab,
      name: 'Privacy',
      icon: ShieldCheckIcon,
      description: 'GDPR compliance and data protection'
    },
    {
      id: 'utilities' as AdminTab,
      name: 'Utilities',
      icon: CogIcon,
      description: 'Research tools and validation'
    },
    {
      id: 'debug' as AdminTab,
      name: 'Debug Data',
      icon: BeakerIcon,
      description: 'Test API endpoints and diagnose data issues'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'participants':
        return <ParticipantManager />;
      case 'monitoring':
        return <ParticipantMonitoringDashboard />;
      case 'comprehensive':
        return <ComprehensiveAnalyticsDashboard />;
      case 'effectiveness':
        return <LearningEffectivenessDashboard />;
      case 'analytics':
        return <AnalyticsDashboard />;
      case 'research':
        return <ResearchAnalyticsDashboard />;
      case 'visualization':
        return <ResearchDataVisualization />;
      case 'test':
        return <TestDataVisualization />;
      case 'export':
        return <div className="p-6">Data export functionality coming soon...</div>;
      case 'privacy':
        return <div className="p-6">Privacy compliance tools coming soon...</div>;
      case 'utilities':
        return <div className="p-6">Research utilities coming soon...</div>;
      case 'debug':
        return <DataDebugger />;
      default:
        return <ComprehensiveAnalyticsDashboard />;
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