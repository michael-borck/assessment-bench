import { useState } from 'react'
import { FileText, Settings, BarChart3, TestTube, GitCompare } from 'lucide-react'
import ProjectManager from './components/ProjectManager'
import TestingLab from './components/TestingLab'
import ResultsDashboard from './components/ResultsDashboard'
import ComparisonDashboard from './components/ComparisonDashboard'

function App() {
  const [activeTab, setActiveTab] = useState('projects')

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">AssessmentBench</h1>
              <p className="text-sm text-gray-500">Research-grade AI grading benchmarks</p>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <nav className="w-64 bg-white border-r border-gray-200 p-4">
          <div className="space-y-2">
            <button
              onClick={() => setActiveTab('projects')}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 ${
                activeTab === 'projects' 
                  ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Projects</span>
            </button>
            
            <button
              onClick={() => setActiveTab('testing')}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 ${
                activeTab === 'testing' 
                  ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <TestTube className="w-4 h-4" />
              <span>Testing Lab</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 ${
                activeTab === 'analytics' 
                  ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </button>
            
            <button
              onClick={() => setActiveTab('comparison')}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 ${
                activeTab === 'comparison' 
                  ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <GitCompare className="w-4 h-4" />
              <span>Comparison</span>
            </button>
            
            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 ${
                activeTab === 'settings' 
                  ? 'bg-primary-50 text-primary-700 border border-primary-200' 
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </button>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 overflow-auto p-6">
          {activeTab === 'projects' && <ProjectManager />}
          
          {activeTab === 'testing' && <TestingLab />}

          {activeTab === 'analytics' && <ResultsDashboard />}
          
          {activeTab === 'comparison' && <ComparisonDashboard />}

          {activeTab === 'settings' && (
            <div className="max-w-4xl mx-auto">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">Settings</h2>
                <p className="text-gray-600">Configure LLM providers and application preferences</p>
              </div>
              
              <div className="grid gap-6">
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">LLM Providers</h3>
                  <div className="text-center py-8">
                    <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Configure your LLM providers to start grading</p>
                    <button className="mt-4 bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600">
                      Add Provider
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App