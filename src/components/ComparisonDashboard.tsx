import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, ScatterChart, Scatter, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { GitCompare, TrendingUp, Target, Zap, Award, AlertCircle } from 'lucide-react';

interface ProviderComparison {
  provider: string;
  model: string;
  averageScore: number;
  reliability: number;
  consistency: number;
  speed: number;
  cost: number;
  totalAssessments: number;
  gradeDistribution: { [key: string]: number };
}

interface ComparisonMetric {
  metric: string;
  openai: number;
  anthropic: number;
  ollama: number;
}

const ComparisonDashboard: React.FC = () => {
  const [selectedProviders, setSelectedProviders] = useState<string[]>(['OpenAI', 'Anthropic']);
  const [comparisonData, setComparisonData] = useState<ProviderComparison[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock comparison data
    const mockComparison: ProviderComparison[] = [
      {
        provider: 'OpenAI',
        model: 'gpt-4o-mini',
        averageScore: 84.2,
        reliability: 0.92,
        consistency: 0.87,
        speed: 0.95,
        cost: 0.72,
        totalAssessments: 156,
        gradeDistribution: { 'A': 23, 'B': 45, 'C': 18, 'D': 8, 'F': 2 }
      },
      {
        provider: 'Anthropic',
        model: 'claude-3-haiku',
        averageScore: 86.1,
        reliability: 0.89,
        consistency: 0.91,
        speed: 0.88,
        cost: 0.85,
        totalAssessments: 124,
        gradeDistribution: { 'A': 31, 'B': 38, 'C': 22, 'D': 11, 'F': 2 }
      },
      {
        provider: 'Ollama',
        model: 'llama3.2',
        averageScore: 79.3,
        reliability: 0.78,
        consistency: 0.73,
        speed: 0.62,
        cost: 1.0,
        totalAssessments: 89,
        gradeDistribution: { 'A': 18, 'B': 35, 'C': 28, 'D': 15, 'F': 4 }
      }
    ];
    
    setComparisonData(mockComparison);
    setLoading(false);
  }, []);

  // Transform data for radar chart
  const radarData = [
    { metric: 'Accuracy', OpenAI: 84, Anthropic: 86, Ollama: 79 },
    { metric: 'Reliability', OpenAI: 92, Anthropic: 89, Ollama: 78 },
    { metric: 'Consistency', OpenAI: 87, Anthropic: 91, Ollama: 73 },
    { metric: 'Speed', OpenAI: 95, Anthropic: 88, Ollama: 62 },
    { metric: 'Cost Efficiency', OpenAI: 72, Anthropic: 85, Ollama: 100 }
  ];

  // Performance comparison data
  const performanceData = comparisonData.map(provider => ({
    provider: provider.provider,
    accuracy: provider.averageScore,
    reliability: provider.reliability * 100,
    consistency: provider.consistency * 100,
    assessments: provider.totalAssessments
  }));

  // Grade distribution comparison
  const gradeComparisonData = ['A', 'B', 'C', 'D', 'F'].map(grade => {
    const data: any = { grade };
    comparisonData.forEach(provider => {
      data[provider.provider] = provider.gradeDistribution[grade] || 0;
    });
    return data;
  });

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            <GitCompare className="w-6 h-6" />
            Provider Comparison
          </h2>
          <p className="text-gray-600">Compare performance across different LLM providers</p>
        </div>

        {/* Provider Selection */}
        <div className="flex gap-2">
          {['OpenAI', 'Anthropic', 'Ollama'].map(provider => (
            <button
              key={provider}
              onClick={() => {
                if (selectedProviders.includes(provider)) {
                  setSelectedProviders(prev => prev.filter(p => p !== provider));
                } else {
                  setSelectedProviders(prev => [...prev, provider]);
                }
              }}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                selectedProviders.includes(provider)
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {provider}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-blue-500" />
            <span className="text-sm font-medium text-gray-600">Best Accuracy</span>
          </div>
          <div className="text-2xl font-semibold text-gray-900">86.1%</div>
          <div className="text-sm text-green-600">Anthropic Claude</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-4 h-4 text-green-500" />
            <span className="text-sm font-medium text-gray-600">Most Reliable</span>
          </div>
          <div className="text-2xl font-semibold text-gray-900">92%</div>
          <div className="text-sm text-blue-600">OpenAI GPT-4</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-yellow-500" />
            <span className="text-sm font-medium text-gray-600">Fastest</span>
          </div>
          <div className="text-2xl font-semibold text-gray-900">0.8s</div>
          <div className="text-sm text-blue-600">OpenAI GPT-4</div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-purple-500" />
            <span className="text-sm font-medium text-gray-600">Most Consistent</span>
          </div>
          <div className="text-2xl font-semibold text-gray-900">91%</div>
          <div className="text-sm text-green-600">Anthropic Claude</div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Radar Chart */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Radar</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" className="text-sm" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} className="text-xs" />
              <Radar
                name="OpenAI"
                dataKey="OpenAI"
                stroke="#3B82F6"
                fill="#3B82F6"
                fillOpacity={0.1}
                strokeWidth={2}
              />
              <Radar
                name="Anthropic"
                dataKey="Anthropic"
                stroke="#10B981"
                fill="#10B981"
                fillOpacity={0.1}
                strokeWidth={2}
              />
              <Radar
                name="Ollama"
                dataKey="Ollama"
                stroke="#F59E0B"
                fill="#F59E0B"
                fillOpacity={0.1}
                strokeWidth={2}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Accuracy vs Reliability Scatter */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Accuracy vs Reliability</h3>
          <ResponsiveContainer width="100%" height={300}>
            <ScatterChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="accuracy" 
                domain={[75, 90]} 
                label={{ value: 'Accuracy (%)', position: 'bottom' }}
              />
              <YAxis 
                dataKey="reliability" 
                domain={[70, 95]} 
                label={{ value: 'Reliability (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip formatter={(value, name) => [`${value}%`, name]} />
              <Scatter name="Providers" dataKey="reliability" fill="#3B82F6">
                {performanceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Grade Distribution Comparison */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Grade Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={gradeComparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="grade" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="OpenAI" fill="#3B82F6" />
              <Bar dataKey="Anthropic" fill="#10B981" />
              <Bar dataKey="Ollama" fill="#F59E0B" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Cost vs Performance */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={performanceData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="provider" type="category" width={80} />
              <Tooltip />
              <Legend />
              <Bar dataKey="accuracy" fill="#3B82F6" name="Accuracy %" />
              <Bar dataKey="consistency" fill="#10B981" name="Consistency %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Comparison Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Detailed Comparison</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reliability</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Consistency</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assessments</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Grade Distribution</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {comparisonData.map((provider, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        provider.provider === 'OpenAI' ? 'bg-blue-500' :
                        provider.provider === 'Anthropic' ? 'bg-green-500' : 'bg-yellow-500'
                      }`}></div>
                      <span className="text-sm font-medium text-gray-900">{provider.provider}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{provider.model}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {provider.averageScore.toFixed(1)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`px-2 py-1 text-xs font-medium rounded-full ${
                        provider.reliability >= 0.9 ? 'bg-green-100 text-green-800' :
                        provider.reliability >= 0.8 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {(provider.reliability * 100).toFixed(0)}%
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${provider.consistency * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500">{(provider.consistency * 100).toFixed(0)}%</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{provider.totalAssessments}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-1">
                      {Object.entries(provider.gradeDistribution).map(([grade, count]) => (
                        <div key={grade} className="text-xs">
                          <span className="font-medium">{grade}:</span>
                          <span className="text-gray-600">{count}</span>
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <h4 className="font-medium text-blue-900 mb-2">Recommendations</h4>
            <ul className="space-y-1 text-sm text-blue-800">
              <li>• <strong>For highest accuracy:</strong> Use Anthropic Claude-3-Haiku (86.1% average score)</li>
              <li>• <strong>For most reliable results:</strong> Use OpenAI GPT-4o-mini (92% reliability)</li>
              <li>• <strong>For cost-effective grading:</strong> Use Ollama Llama3.2 (free, local deployment)</li>
              <li>• <strong>For consistent results:</strong> Use Anthropic Claude-3-Haiku (91% consistency)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComparisonDashboard;