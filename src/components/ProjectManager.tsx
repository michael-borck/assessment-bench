import React, { useEffect, useState } from 'react';
import { useProjectStore } from '../stores/projectStore';
import { Plus, Trash2, Settings, FileText, AlertCircle } from 'lucide-react';

const ProjectManager: React.FC = () => {
  const {
    projects,
    providers,
    loading,
    error,
    fetchProjects,
    createProject,
    deleteProject,
    fetchProviders,
    addProvider,
    clearError,
  } = useProjectStore();

  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showAddProvider, setShowAddProvider] = useState(false);
  const [projectForm, setProjectForm] = useState({ name: '', description: '' });
  const [providerForm, setProviderForm] = useState({ 
    name: '', 
    provider_type: 'openai', 
    model: 'gpt-4' 
  });

  useEffect(() => {
    fetchProjects();
    fetchProviders();
  }, [fetchProjects, fetchProviders]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (projectForm.name.trim()) {
      await createProject(projectForm.name, projectForm.description || undefined);
      setProjectForm({ name: '', description: '' });
      setShowCreateProject(false);
    }
  };

  const handleAddProvider = async (e: React.FormEvent) => {
    e.preventDefault();
    if (providerForm.name.trim()) {
      await addProvider(providerForm.name, providerForm.provider_type, providerForm.model);
      setProviderForm({ name: '', provider_type: 'openai', model: 'gpt-4' });
      setShowAddProvider(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-error-50 border border-error-200 rounded-lg flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-error-600" />
          <div className="flex-1">
            <p className="text-error-800">{error}</p>
          </div>
          <button
            onClick={clearError}
            className="text-error-600 hover:text-error-800"
          >
            ×
          </button>
        </div>
      )}

      {/* Projects Section */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">Assessment Projects</h2>
            <p className="text-gray-600">Manage your grading research projects</p>
          </div>
          <button
            onClick={() => setShowCreateProject(true)}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </button>
        </div>

        {/* Create Project Modal */}
        {showCreateProject && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg w-96">
              <h3 className="text-lg font-semibold mb-4">Create New Project</h3>
              <form onSubmit={handleCreateProject}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={projectForm.name}
                    onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Enter project name"
                    required
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={projectForm.description}
                    onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={3}
                    placeholder="Describe your research project"
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-primary-500 text-white py-2 px-4 rounded-lg hover:bg-primary-600 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Project'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowCreateProject(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Projects Grid */}
        {loading && projects.length === 0 ? (
          <div className="text-center py-8 text-gray-500">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
            <p className="text-gray-600 mb-6">Create your first assessment project to get started</p>
            <button
              onClick={() => setShowCreateProject(true)}
              className="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600"
            >
              Create Project
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {projects.map((project) => (
              <div key={project.id} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {project.name}
                    </h3>
                    {project.description && (
                      <p className="text-gray-600 text-sm">{project.description}</p>
                    )}
                  </div>
                  <button
                    onClick={() => deleteProject(project.id)}
                    className="text-gray-400 hover:text-error-600"
                    title="Delete project"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">ID: {project.id.slice(0, 8)}...</span>
                  <button className="text-primary-600 hover:text-primary-800 text-sm font-medium">
                    Open →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Providers Section */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900">LLM Providers</h2>
            <p className="text-gray-600">Configure your AI model providers</p>
          </div>
          <button
            onClick={() => setShowAddProvider(true)}
            className="bg-accent-500 text-white px-4 py-2 rounded-lg hover:bg-accent-600 flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Add Provider</span>
          </button>
        </div>

        {/* Add Provider Modal */}
        {showAddProvider && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg w-96">
              <h3 className="text-lg font-semibold mb-4">Add LLM Provider</h3>
              <form onSubmit={handleAddProvider}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider Name
                  </label>
                  <input
                    type="text"
                    value={providerForm.name}
                    onChange={(e) => setProviderForm({ ...providerForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
                    placeholder="e.g., OpenAI GPT-4"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Provider Type
                  </label>
                  <select
                    value={providerForm.provider_type}
                    onChange={(e) => setProviderForm({ ...providerForm, provider_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="google">Google</option>
                    <option value="ollama">Ollama</option>
                  </select>
                </div>
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Model
                  </label>
                  <input
                    type="text"
                    value={providerForm.model}
                    onChange={(e) => setProviderForm({ ...providerForm, model: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-500"
                    placeholder="e.g., gpt-4, claude-3-opus"
                    required
                  />
                </div>
                <div className="flex space-x-3">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-accent-500 text-white py-2 px-4 rounded-lg hover:bg-accent-600 disabled:opacity-50"
                  >
                    {loading ? 'Adding...' : 'Add Provider'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddProvider(false)}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Providers Grid */}
        {providers.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Settings className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No providers configured</h3>
            <p className="text-gray-600 mb-6">Add your first LLM provider to start grading</p>
            <button
              onClick={() => setShowAddProvider(true)}
              className="bg-accent-500 text-white px-6 py-2 rounded-lg hover:bg-accent-600"
            >
              Add Provider
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {providers.map((provider) => (
              <div key={provider.id} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {provider.name}
                    </h3>
                    <p className="text-gray-600 text-sm capitalize">{provider.provider_type}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">ID: {provider.id.slice(0, 8)}...</span>
                  <button className="text-accent-600 hover:text-accent-800 text-sm font-medium">
                    Configure
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectManager;