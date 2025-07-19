import React, { useState } from 'react';
import { researchApi } from '../../services/api';
import { ExclamationTriangleIcon, CheckCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface DebugResult {
  endpoint: string;
  status: 'success' | 'error' | 'loading';
  data?: any;
  error?: string;
  count?: number;
}

const DataDebugger: React.FC = () => {
  const [results, setResults] = useState<DebugResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const endpoints = [
    { name: 'Dashboard Overview', fn: () => researchApi.getDashboardOverview() },
    { name: 'Activity Timeline', fn: () => researchApi.getActivityTimeline(30) },
    { name: 'Learning Effectiveness', fn: () => researchApi.getLearningEffectivenessData() },
    { name: 'All Participants', fn: () => researchApi.getAllParticipants() },
    { name: 'Study Statistics', fn: () => researchApi.getStudyStatistics() },
  ];

  const runDiagnostics = async () => {
    setIsRunning(true);
    setResults([]);

    for (const endpoint of endpoints) {
      const result: DebugResult = {
        endpoint: endpoint.name,
        status: 'loading'
      };
      
      setResults(prev => [...prev, result]);

      try {
        const response = await endpoint.fn();
        const data = response.data;
        
        let count = 0;
        if (Array.isArray(data)) {
          count = data.length;
        } else if (data && typeof data === 'object') {
          if (data.learning_metrics) count = data.learning_metrics.length;
          else if (data.total_participants !== undefined) count = data.total_participants;
          else count = Object.keys(data).length;
        }

        const successResult: DebugResult = {
          endpoint: endpoint.name,
          status: 'success',
          data: data,
          count: count
        };

        setResults(prev => prev.map(r => 
          r.endpoint === endpoint.name ? successResult : r
        ));

      } catch (error: any) {
        const errorResult: DebugResult = {
          endpoint: endpoint.name,
          status: 'error',
          error: error.response?.data?.error || error.message || 'Unknown error'
        };

        setResults(prev => prev.map(r => 
          r.endpoint === endpoint.name ? errorResult : r
        ));
      }
    }

    setIsRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'loading':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return null;
    }
  };

  const getRecommendations = () => {
    const hasData = results.some(r => r.status === 'success' && (r.count || 0) > 0);
    const hasErrors = results.some(r => r.status === 'error');

    if (!hasData && hasErrors) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-red-800 mb-2">🔧 Fix Required</h3>
          <div className="text-sm text-red-700 space-y-1">
            <p><strong>Backend Issues Detected:</strong></p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>Make sure Django server is running: <code className="bg-red-100 px-1 rounded">python manage.py runserver 8001</code></li>
              <li>Check if you're logged in as admin user</li>
              <li>Verify database migrations: <code className="bg-red-100 px-1 rounded">python manage.py migrate</code></li>
              <li>Create test data: <code className="bg-red-100 px-1 rounded">python manage.py populate_test_data --participants 50</code></li>
            </ol>
          </div>
        </div>
      );
    }

    if (!hasData) {
      return (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-800 mb-2">📊 No Data Found</h3>
          <div className="text-sm text-yellow-700 space-y-1">
            <p><strong>Create test data to populate dashboards:</strong></p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>Run: <code className="bg-yellow-100 px-1 rounded">python manage.py populate_test_data --participants 50</code></li>
              <li>Create sample study: <code className="bg-yellow-100 px-1 rounded">python manage.py create_sample_study</code></li>
              <li>Refresh this page after creating data</li>
            </ol>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-green-800 mb-2">✅ Data Available</h3>
        <p className="text-sm text-green-700">
          Your dashboards should now display data. If they're still empty, check browser console for JavaScript errors.
        </p>
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard Data Diagnostics</h1>
            <p className="text-gray-600">Test API endpoints and check data availability</p>
          </div>
          <button
            onClick={runDiagnostics}
            disabled={isRunning}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <ArrowPathIcon className={`h-4 w-4 ${isRunning ? 'animate-spin' : ''}`} />
            <span>{isRunning ? 'Testing...' : 'Run Diagnostics'}</span>
          </button>
        </div>

        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-800">API Endpoint Results:</h2>
            
            <div className="space-y-2">
              {results.map((result, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(result.status)}
                    <span className="font-medium">{result.endpoint}</span>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    {result.status === 'success' && (
                      <span className="text-green-600">
                        {result.count !== undefined ? `${result.count} items` : 'Success'}
                      </span>
                    )}
                    {result.status === 'error' && (
                      <span className="text-red-600">Error: {result.error}</span>
                    )}
                    {result.status === 'loading' && (
                      <span className="text-blue-600">Testing...</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {!isRunning && (
              <div className="mt-6">
                {getRecommendations()}
              </div>
            )}

            {!isRunning && results.some(r => r.status === 'success') && (
              <div className="mt-6 bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-800 mb-3">📊 Data Summary:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.filter(r => r.status === 'success').map((result, index) => (
                    <div key={index} className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-700">{result.endpoint}</div>
                      <div className="text-sm text-gray-500">
                        {result.count !== undefined ? `${result.count} records` : 'Data available'}
                      </div>
                      {result.data && typeof result.data === 'object' && (
                        <div className="text-xs text-gray-400 mt-1">
                          Fields: {Object.keys(result.data).length}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {results.length === 0 && !isRunning && (
          <div className="text-center py-8 text-gray-500">
            Click "Run Diagnostics" to test your dashboard data availability
          </div>
        )}
      </div>
    </div>
  );
};

export default DataDebugger;