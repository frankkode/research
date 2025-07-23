import React from 'react';
import {
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const TestDataVisualization: React.FC = () => {
  // Sample data to test if visualization is working
  const sampleData = [
    { name: 'ChatGPT Group', preQuiz: 65, postQuiz: 82, participants: 12 },
    { name: 'PDF Group', preQuiz: 58, postQuiz: 75, participants: 12 }
  ];

  const completionData = [
    { name: 'Completed', value: 18 },
    { name: 'In Progress', value: 4 },
    { name: 'Not Started', value: 2 }
  ];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">Test Data Visualization</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Quiz Score Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sampleData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="preQuiz" fill="#8884d8" name="Pre-Quiz Score" />
              <Bar dataKey="postQuiz" fill="#82ca9d" name="Post-Quiz Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Study Completion Status</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={completionData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({name, value}) => `${name}: ${value}`}
              >
                {completionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6 bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Key Research Findings</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">+17%</div>
            <div className="text-sm text-gray-600">ChatGPT Learning Gain</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">+17%</div>
            <div className="text-sm text-gray-600">PDF Learning Gain</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">75%</div>
            <div className="text-sm text-gray-600">Overall Completion Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestDataVisualization;