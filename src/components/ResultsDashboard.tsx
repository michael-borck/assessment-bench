import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, ScatterChart, Scatter } from 'recharts';
import { TrendingUp, TrendingDown, BarChart3, Activity, Target, Users, Clock, CheckCircle, AlertTriangle, FileText, Download, Filter } from 'lucide-react';
import { exportResults, ExportOptions } from '../utils/exportUtils';

interface GradingResult {
  id: string;
  provider: string;
  model: string;
  grade: string | null;
  score: number | null;
  reliability: number;
  timestamp: Date;
  strengths: string[];
  improvements: string[];
  consistency: 'high' | 'medium' | 'low';
}

interface StatCard {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
}

const ResultsDashboard: React.FC = () => {
  // Mock data - In real app, this would come from API
  const [results, setResults] = useState<GradingResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedProvider, setSelectedProvider] = useState('all');
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    // Simulate loading data
    const mockResults: GradingResult[] = [
      {
        id: '1',
        provider: 'OpenAI',
        model: 'gpt-4o-mini',
        grade: 'B+',
        score: 87,
        reliability: 0.92,
        timestamp: new Date('2024-01-15T10:30:00Z'),
        strengths: ['Clear writing', 'Good structure'],
        improvements: ['More examples needed', 'Expand conclusion'],
        consistency: 'high'
      },
      {
        id: '2',
        provider: 'OpenAI',
        model: 'gpt-4o-mini',
        grade: 'A-',
        score: 91,
        reliability: 0.88,
        timestamp: new Date('2024-01-15T11:15:00Z'),
        strengths: ['Excellent analysis', 'Strong evidence'],
        improvements: ['Minor formatting issues'],
        consistency: 'high'
      },
      {
        id: '3',
        provider: 'Anthropic',
        model: 'claude-3-haiku',
        grade: 'B',
        score: 83,
        reliability: 0.85,
        timestamp: new Date('2024-01-15T14:20:00Z'),
        strengths: ['Good organization'],
        improvements: ['Needs more detail', 'Weak conclusion'],
        consistency: 'medium'
      },
      {
        id: '4',
        provider: 'OpenAI',
        model: 'gpt-4o-mini',
        grade: 'A',
        score: 94,
        reliability: 0.95,
        timestamp: new Date('2024-01-16T09:45:00Z'),
        strengths: ['Outstanding work', 'Perfect structure', 'Excellent examples'],
        improvements: [],
        consistency: 'high'
      },
      {
        id: '5',
        provider: 'Ollama',
        model: 'llama3.1',
        grade: 'C+',
        score: 77,
        reliability: 0.72,
        timestamp: new Date('2024-01-16T15:30:00Z'),
        strengths: ['Basic understanding'],
        improvements: ['Lacks depth', 'Poor organization', 'Grammar issues'],
        consistency: 'low'
      }
    ];

    setTimeout(() => {
      setResults(mockResults);
      setLoading(false);
    }, 1000);
  }, []);

  // Calculate statistics
  const stats = React.useMemo(() => {
    if (results.length === 0) return null;

    const validScores = results.filter(r => r.score !== null).map(r => r.score as number);
    const avgScore = validScores.length > 0 ? validScores.reduce((a, b) => a + b, 0) / validScores.length : 0;
    const avgReliability = results.reduce((a, b) => a + b.reliability, 0) / results.length;
    const highConsistency = results.filter(r => r.consistency === 'high').length;
    const consistencyRate = (highConsistency / results.length) * 100;

    const providerStats = results.reduce((acc, result) => {
      if (!acc[result.provider]) {
        acc[result.provider] = { count: 0, avgScore: 0, totalScore: 0 };
      }
      acc[result.provider].count++;
      if (result.score) {
        acc[result.provider].totalScore += result.score;
        acc[result.provider].avgScore = acc[result.provider].totalScore / acc[result.provider].count;
      }
      return acc;
    }, {} as Record<string, { count: number; avgScore: number; totalScore: number }>);

    return {
      totalAssessments: results.length,
      avgScore: Math.round(avgScore * 10) / 10,
      avgReliability: Math.round(avgReliability * 100) / 100,
      consistencyRate: Math.round(consistencyRate * 10) / 10,
      providerStats
    };
  }, [results]);

  const chartData = React.useMemo(() => {
    if (!stats) return [];
    
    return Object.entries(stats.providerStats).map(([provider, data]) => ({
      provider,
      avgScore: Math.round(data.avgScore * 10) / 10,
      count: data.count,
      reliability: results.filter(r => r.provider === provider)
        .reduce((acc, r) => acc + r.reliability, 0) / data.count
    }));
  }, [results, stats]);

  const timeSeriesData = React.useMemo(() => {
    return results
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .map((result, index) => ({
        assessment: index + 1,
        score: result.score || 0,
        reliability: result.reliability * 100,
        provider: result.provider,
        timestamp: result.timestamp.toLocaleDateString()
      }));
  }, [results]);

  const gradeDistribution = React.useMemo(() => {
    const distribution: Record<string, number> = {};
    results.forEach(result => {
      if (result.grade) {
        distribution[result.grade] = (distribution[result.grade] || 0) + 1;
      }
    });
    
    return Object.entries(distribution).map(([grade, count]) => ({
      grade,
      count,
      percentage: Math.round((count / results.length) * 100)
    }));
  }, [results]);

  const consistencyData = React.useMemo(() => {
    const consistency = { high: 0, medium: 0, low: 0 };
    results.forEach(result => {
      consistency[result.consistency]++;
    });
    
    return [
      { name: 'High', value: consistency.high, color: '#10B981' },
      { name: 'Medium', value: consistency.medium, color: '#F59E0B' },
      { name: 'Low', value: consistency.low, color: '#EF4444' }
    ];
  }, [results]);

  const statCards: StatCard[] = [
    {
      title: 'Total Assessments',
      value: stats?.totalAssessments || 0,
      icon: <FileText className="w-5 h-5" />,
      color: 'blue'
    },
    {
      title: 'Average Score',
      value: `${stats?.avgScore || 0}%`,
      change: 2.4,
      icon: <Target className="w-5 h-5" />,
      color: 'green'
    },
    {
      title: 'Average Reliability',
      value: `${(stats?.avgReliability || 0) * 100}%`,
      change: -1.2,
      icon: <Activity className="w-5 h-5" />,
      color: 'purple'
    },
    {
      title: 'Consistency Rate',
      value: `${stats?.consistencyRate || 0}%`,
      change: 5.8,
      icon: <CheckCircle className="w-5 h-5" />,
      color: 'emerald'
    }
  ];

  // Export handler
  const handleExport = async (format: 'csv' | 'json' | 'pdf') => {
    try {
      setExportLoading(true);
      
      const options: ExportOptions = {
        format,
        providers: selectedProvider === 'all' ? undefined : [selectedProvider],
      };
      
      // Add date range filter based on selection
      if (selectedTimeRange !== 'all') {
        const now = new Date();
        const daysBack = selectedTimeRange === '1d' ? 1 : selectedTimeRange === '7d' ? 7 : 30;
        const startDate = new Date(now.getTime() - daysBack * 24 * 60 * 60 * 1000);
        
        options.dateRange = {
          start: startDate,
          end: now
        };
      }
      
      await exportResults(results, options);
      setShowExportModal(false);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExportLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-64 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-80 bg-gray-200 rounded-lg"></div>
            <div className="h-80 bg-gray-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Results Dashboard</h1>
            <p className="text-gray-600">Comprehensive analysis of AI grading performance</p>
          </div>
          
          {/* Filters and Export */}
          <div className="flex items-center space-x-4">
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="1d">Last 24 hours</option>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="all">All time</option>
            </select>
            
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Providers</option>
              <option value="OpenAI">OpenAI</option>
              <option value="Anthropic">Anthropic</option>
              <option value="Ollama">Ollama</option>
            </select>
            
            <button
              onClick={() => setShowExportModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                {stat.change && (
                  <div className="flex items-center mt-2">
                    {stat.change > 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-500" />
                    )}
                    <span className={`text-sm ml-1 ${stat.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {Math.abs(stat.change)}%
                    </span>
                  </div>
                )}
              </div>
              <div className={`p-3 rounded-full bg-${stat.color}-100`}>
                <div className={`text-${stat.color}-600`}>
                  {stat.icon}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Provider Performance Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Provider Performance Comparison
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="provider" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'avgScore' ? `${value}%` : value,
                  name === 'avgScore' ? 'Average Score' : name === 'count' ? 'Assessments' : 'Reliability'
                ]}
              />
              <Legend />
              <Bar dataKey="avgScore" fill="#3B82F6" name="Avg Score" />
              <Bar dataKey="count" fill="#10B981" name="Assessments" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Score Trends Over Time */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Score Trends Over Time
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="assessment" />
              <YAxis />
              <Tooltip 
                labelFormatter={(label) => `Assessment ${label}`}
                formatter={(value, name) => [
                  name === 'score' ? `${value}%` : `${value}%`,
                  name === 'score' ? 'Score' : 'Reliability'
                ]}
              />
              <Legend />
              <Line type="monotone" dataKey="score" stroke="#3B82F6" name="Score" strokeWidth={2} />
              <Line type="monotone" dataKey="reliability" stroke="#8B5CF6" name="Reliability" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Row Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Grade Distribution */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Grade Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={gradeDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="grade" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}`, 'Count']} />
              <Bar dataKey="count" fill="#F59E0B" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Consistency Analysis */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Grading Consistency</h3>
          <div className="flex items-center justify-center h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={consistencyData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, value, percentage }) => `${name}: ${value} (${((value / results.length) * 100).toFixed(1)}%)`}
                >
                  {consistencyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Results Table */}
      <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Assessments</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Provider/Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Grade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reliability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Consistency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.slice(0, 10).map((result) => (
                <tr key={result.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{result.provider}</div>
                      <div className="text-sm text-gray-500">{result.model}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                      {result.grade || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {result.score ? `${result.score}%` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm text-gray-900">{(result.reliability * 100).toFixed(1)}%</div>
                      <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${result.reliability * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      result.consistency === 'high' ? 'bg-green-100 text-green-800' :
                      result.consistency === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {result.consistency}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {result.timestamp.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Results</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => handleExport('csv')}
                    disabled={exportLoading}
                    className="flex items-center justify-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                  >
                    <FileText className="w-4 h-4" />
                    CSV
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    disabled={exportLoading}
                    className="flex items-center justify-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                  >
                    <FileText className="w-4 h-4" />
                    JSON
                  </button>
                  <button
                    onClick={() => handleExport('pdf')}
                    disabled={exportLoading}
                    className="flex items-center justify-center gap-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                  >
                    <FileText className="w-4 h-4" />
                    PDF
                  </button>
                </div>
              </div>
              
              {exportLoading && (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500"></div>
                  <span className="ml-2 text-gray-600">Exporting...</span>
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowExportModal(false)}
                disabled={exportLoading}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDashboard;