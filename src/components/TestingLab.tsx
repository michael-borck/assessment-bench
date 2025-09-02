import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { TestTube, Play, BarChart3, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { useProjectStore } from '../stores/projectStore';

interface TestLLMResponse {
  success: boolean;
  response?: string;
  tokens_used?: number;
  model: string;
}

interface TestGradingResponse {
  success: boolean;
  overall_grade?: string;
  total_points?: number;
  summary_feedback?: string;
  strengths: string[];
  improvements: string[];
  raw_response: string;
}

interface MultipleRunsResponse {
  success: boolean;
  run_count: number;
  mean_score: number;
  median_score: number;
  std_deviation: number;
  coefficient_of_variation: number;
  score_range: number;
  reliability_score: number;
  individual_grades: (string | null)[];
  individual_scores: (number | null)[];
  common_strengths: string[];
  common_improvements: string[];
  individual_responses: string[];
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

const TestingLab: React.FC = () => {
  const { providers, fetchProviders } = useProjectStore();
  const [activeTest, setActiveTest] = useState<'provider' | 'grading' | 'multiple'>('provider');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Provider test state
  const [providerTest, setProviderTest] = useState({
    provider_id: '',
    api_key: '',
    prompt: 'Hello, can you help me test this connection?'
  });
  const [providerResult, setProviderResult] = useState<TestLLMResponse | null>(null);
  
  // Grading test state
  const [gradingTest, setGradingTest] = useState({
    provider_id: '',
    api_key: '',
    submission_text: 'This essay discusses the importance of renewable energy sources in combating climate change. Solar and wind power offer sustainable alternatives to fossil fuels. The transition to clean energy requires government support and technological innovation.',
    rubric: `GRADING RUBRIC (100 points total):
1. Content & Understanding (40 points)
   - Demonstrates clear understanding of topic
   - Provides relevant examples and evidence
   
2. Organization & Structure (30 points)
   - Clear introduction, body, and conclusion
   - Logical flow of ideas
   
3. Writing Quality (30 points)
   - Grammar and spelling
   - Clarity and coherence`
  });
  const [gradingResult, setGradingResult] = useState<TestGradingResponse | null>(null);
  
  // Multiple runs test state
  const [multipleTest, setMultipleTest] = useState({
    provider_id: '',
    api_key: '',
    submission_text: 'This essay explores the impact of artificial intelligence on modern education. AI tutoring systems can provide personalized learning experiences. However, concerns about academic integrity and human connection in education remain significant challenges.',
    rubric: `GRADING RUBRIC (100 points total):
1. Thesis & Argumentation (50 points)
   - Clear thesis statement
   - Strong supporting arguments
   
2. Evidence & Examples (30 points)
   - Relevant supporting evidence
   - Proper use of examples
   
3. Writing Mechanics (20 points)
   - Grammar, spelling, punctuation
   - Professional presentation`,
    num_runs: 3
  });
  const [multipleResult, setMultipleResult] = useState<MultipleRunsResponse | null>(null);

  useEffect(() => {
    fetchProviders();
  }, [fetchProviders]);

  const testProvider = async () => {
    if (!providerTest.provider_id || !providerTest.api_key || !providerTest.prompt) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    setProviderResult(null);

    try {
      const response = await invoke<ApiResponse<TestLLMResponse>>('test_llm_provider', {
        request: providerTest
      });

      if (response.success && response.data) {
        setProviderResult(response.data);
      } else {
        setError(response.error || 'Provider test failed');
      }
    } catch (err) {
      setError(`Failed to test provider: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const testGrading = async () => {
    if (!gradingTest.provider_id || !gradingTest.api_key || !gradingTest.submission_text || !gradingTest.rubric) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    setGradingResult(null);

    try {
      const response = await invoke<ApiResponse<TestGradingResponse>>('test_basic_grading', {
        request: gradingTest
      });

      if (response.success && response.data) {
        setGradingResult(response.data);
      } else {
        setError(response.error || 'Grading test failed');
      }
    } catch (err) {
      setError(`Failed to test grading: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const testMultipleRuns = async () => {
    if (!multipleTest.provider_id || !multipleTest.api_key || !multipleTest.submission_text || !multipleTest.rubric) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);
    setMultipleResult(null);

    try {
      const response = await invoke<ApiResponse<MultipleRunsResponse>>('test_multiple_grading_runs', {
        request: multipleTest
      });

      if (response.success && response.data) {
        setMultipleResult(response.data);
      } else {
        setError(response.error || 'Multiple runs test failed');
      }
    } catch (err) {
      setError(`Failed to test multiple runs: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Testing Lab</h2>
        <p className="text-gray-600">Test LLM providers and grading functionality</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <div className="flex-1">
            <p className="text-red-800">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800"
          >
            ×
          </button>
        </div>
      )}

      {/* Test Type Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTest('provider')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTest === 'provider'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Provider Test
            </button>
            <button
              onClick={() => setActiveTest('grading')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTest === 'grading'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Single Grading
            </button>
            <button
              onClick={() => setActiveTest('multiple')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTest === 'multiple'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Multiple Runs
            </button>
          </nav>
        </div>
      </div>

      {/* Provider Test */}
      {activeTest === 'provider' && (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <TestTube className="w-5 h-5" />
              <span>Test LLM Provider</span>
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Provider</label>
                <select
                  value={providerTest.provider_id}
                  onChange={(e) => setProviderTest({ ...providerTest, provider_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select a provider</option>
                  {providers.map((provider) => (
                    <option key={provider.id} value={provider.id}>
                      {provider.name} ({provider.provider_type})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                <input
                  type="password"
                  value={providerTest.api_key}
                  onChange={(e) => setProviderTest({ ...providerTest, api_key: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Enter your API key"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Test Prompt</label>
                <textarea
                  value={providerTest.prompt}
                  onChange={(e) => setProviderTest({ ...providerTest, prompt: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  placeholder="Enter a test prompt"
                />
              </div>
              
              <button
                onClick={testProvider}
                disabled={loading}
                className="w-full bg-primary-500 text-white py-2 px-4 rounded-lg hover:bg-primary-600 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>Testing...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Test Provider</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Provider Results */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>
            
            {providerResult ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  {providerResult.success ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  )}
                  <span className={providerResult.success ? 'text-green-600' : 'text-red-600'}>
                    {providerResult.success ? 'Success' : 'Failed'}
                  </span>
                </div>
                
                {providerResult.success && providerResult.response && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Response</label>
                    <div className="p-3 bg-gray-50 rounded-lg text-sm">
                      {providerResult.response}
                    </div>
                  </div>
                )}
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Model:</span>
                    <span className="ml-2 font-medium">{providerResult.model}</span>
                  </div>
                  {providerResult.tokens_used && (
                    <div>
                      <span className="text-gray-600">Tokens:</span>
                      <span className="ml-2 font-medium">{providerResult.tokens_used}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <TestTube className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Run a test to see results</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Grading Test */}
      {activeTest === 'grading' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <TestTube className="w-5 h-5" />
              <span>Test Basic Grading</span>
            </h3>
            
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Provider</label>
                  <select
                    value={gradingTest.provider_id}
                    onChange={(e) => setGradingTest({ ...gradingTest, provider_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select a provider</option>
                    {providers.map((provider) => (
                      <option key={provider.id} value={provider.id}>
                        {provider.name} ({provider.provider_type})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                  <input
                    type="password"
                    value={gradingTest.api_key}
                    onChange={(e) => setGradingTest({ ...gradingTest, api_key: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter your API key"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Submission Text</label>
                  <textarea
                    value={gradingTest.submission_text}
                    onChange={(e) => setGradingTest({ ...gradingTest, submission_text: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={6}
                    placeholder="Enter the student submission to grade"
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rubric</label>
                  <textarea
                    value={gradingTest.rubric}
                    onChange={(e) => setGradingTest({ ...gradingTest, rubric: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={10}
                    placeholder="Enter the grading rubric"
                  />
                </div>
                
                <button
                  onClick={testGrading}
                  disabled={loading}
                  className="w-full bg-green-500 text-white py-2 px-4 rounded-lg hover:bg-green-600 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Grading...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Grade Submission</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Grading Results */}
          {gradingResult && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Grading Results</h3>
              
              <div className="grid gap-6 lg:grid-cols-2">
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    {gradingResult.success ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-red-600" />
                    )}
                    <span className={gradingResult.success ? 'text-green-600' : 'text-red-600'}>
                      {gradingResult.success ? 'Grading Complete' : 'Grading Failed'}
                    </span>
                  </div>
                  
                  {gradingResult.success && (
                    <>
                      <div className="grid grid-cols-2 gap-4">
                        {gradingResult.overall_grade && (
                          <div>
                            <span className="text-sm text-gray-600">Grade:</span>
                            <div className="text-2xl font-bold text-primary-600">{gradingResult.overall_grade}</div>
                          </div>
                        )}
                        {gradingResult.total_points && (
                          <div>
                            <span className="text-sm text-gray-600">Points:</span>
                            <div className="text-2xl font-bold text-primary-600">{gradingResult.total_points}</div>
                          </div>
                        )}
                      </div>
                      
                      {gradingResult.summary_feedback && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Summary Feedback</label>
                          <div className="p-3 bg-blue-50 rounded-lg text-sm">
                            {gradingResult.summary_feedback}
                          </div>
                        </div>
                      )}
                      
                      {gradingResult.strengths.length > 0 && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Strengths</label>
                          <ul className="space-y-1">
                            {gradingResult.strengths.map((strength, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                                <span className="text-sm">{strength}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {gradingResult.improvements.length > 0 && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">Areas for Improvement</label>
                          <ul className="space-y-1">
                            {gradingResult.improvements.map((improvement, index) => (
                              <li key={index} className="flex items-start space-x-2">
                                <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                                <span className="text-sm">{improvement}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Raw Response</label>
                  <div className="p-3 bg-gray-50 rounded-lg text-xs max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap">{gradingResult.raw_response}</pre>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Multiple Runs Test */}
      {activeTest === 'multiple' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <BarChart3 className="w-5 h-5" />
              <span>Test Multiple Grading Runs</span>
            </h3>
            
            <div className="grid gap-6 lg:grid-cols-2">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Provider</label>
                  <select
                    value={multipleTest.provider_id}
                    onChange={(e) => setMultipleTest({ ...multipleTest, provider_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select a provider</option>
                    {providers.map((provider) => (
                      <option key={provider.id} value={provider.id}>
                        {provider.name} ({provider.provider_type})
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                  <input
                    type="password"
                    value={multipleTest.api_key}
                    onChange={(e) => setMultipleTest({ ...multipleTest, api_key: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter your API key"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Number of Runs</label>
                  <input
                    type="number"
                    min="2"
                    max="10"
                    value={multipleTest.num_runs}
                    onChange={(e) => setMultipleTest({ ...multipleTest, num_runs: parseInt(e.target.value) || 3 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Submission Text</label>
                  <textarea
                    value={multipleTest.submission_text}
                    onChange={(e) => setMultipleTest({ ...multipleTest, submission_text: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={5}
                    placeholder="Enter the student submission to grade"
                  />
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rubric</label>
                  <textarea
                    value={multipleTest.rubric}
                    onChange={(e) => setMultipleTest({ ...multipleTest, rubric: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={8}
                    placeholder="Enter the grading rubric"
                  />
                </div>
                
                <button
                  onClick={testMultipleRuns}
                  disabled={loading}
                  className="w-full bg-purple-500 text-white py-2 px-4 rounded-lg hover:bg-purple-600 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader className="w-4 h-4 animate-spin" />
                      <span>Running Multiple Tests...</span>
                    </>
                  ) : (
                    <>
                      <BarChart3 className="w-4 h-4" />
                      <span>Run Multiple Tests</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Multiple Runs Results */}
          {multipleResult && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Multiple Runs Analysis</h3>
              
              <div className="grid gap-6">
                {/* Statistics Overview */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600">{multipleResult.mean_score.toFixed(1)}</div>
                    <div className="text-sm text-blue-600">Mean Score</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600">{multipleResult.median_score.toFixed(1)}</div>
                    <div className="text-sm text-green-600">Median Score</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-yellow-600">{multipleResult.std_deviation.toFixed(1)}</div>
                    <div className="text-sm text-yellow-600">Std Deviation</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-purple-600">{(multipleResult.reliability_score * 100).toFixed(0)}%</div>
                    <div className="text-sm text-purple-600">Reliability</div>
                  </div>
                </div>
                
                {/* Individual Results */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Individual Results</h4>
                  <div className="grid gap-3">
                    {multipleResult.individual_grades.map((grade, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="text-sm font-medium">Run {index + 1}</span>
                        <div className="flex items-center space-x-4">
                          {grade && (
                            <span className="text-sm font-semibold text-primary-600">{grade}</span>
                          )}
                          {multipleResult.individual_scores[index] && (
                            <span className="text-sm text-gray-600">{multipleResult.individual_scores[index]} pts</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Common Feedback */}
                <div className="grid gap-6 lg:grid-cols-2">
                  {multipleResult.common_strengths.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Common Strengths</h4>
                      <ul className="space-y-2">
                        {multipleResult.common_strengths.map((strength, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5" />
                            <span className="text-sm">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {multipleResult.common_improvements.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Common Improvements</h4>
                      <ul className="space-y-2">
                        {multipleResult.common_improvements.map((improvement, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                            <span className="text-sm">{improvement}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TestingLab;