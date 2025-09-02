import { create } from 'zustand';
import { invoke } from '@tauri-apps/api/core';

export interface Project {
  id: string;
  name: string;
  description?: string;
}

export interface Provider {
  id: string;
  name: string;
  provider_type: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

interface ProjectState {
  projects: Project[];
  providers: Provider[];
  loading: boolean;
  error: string | null;
  
  // Actions
  fetchProjects: () => Promise<void>;
  createProject: (name: string, description?: string) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  
  fetchProviders: () => Promise<void>;
  addProvider: (name: string, type: string, model: string) => Promise<void>;
  
  clearError: () => void;
}

export const useProjectStore = create<ProjectState>()((set, get) => ({
  projects: [],
  providers: [],
  loading: false,
  error: null,

  fetchProjects: async () => {
    set({ loading: true, error: null });
    try {
      const response = await invoke<ApiResponse<Project[]>>('list_projects_simple');
      if (response.success && response.data) {
        set({ projects: response.data, loading: false });
      } else {
        set({ error: response.error || 'Failed to fetch projects', loading: false });
      }
    } catch (error) {
      set({ error: `Failed to fetch projects: ${error}`, loading: false });
    }
  },

  createProject: async (name: string, description?: string) => {
    set({ loading: true, error: null });
    try {
      const response = await invoke<ApiResponse<Project>>('create_project_simple', {
        request: { name, description }
      });
      
      if (response.success && response.data) {
        const { projects } = get();
        set({ 
          projects: [response.data, ...projects], 
          loading: false 
        });
      } else {
        set({ error: response.error || 'Failed to create project', loading: false });
      }
    } catch (error) {
      set({ error: `Failed to create project: ${error}`, loading: false });
    }
  },

  deleteProject: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await invoke<ApiResponse<boolean>>('delete_project_simple', { id });
      
      if (response.success) {
        const { projects } = get();
        set({ 
          projects: projects.filter(p => p.id !== id), 
          loading: false 
        });
      } else {
        set({ error: response.error || 'Failed to delete project', loading: false });
      }
    } catch (error) {
      set({ error: `Failed to delete project: ${error}`, loading: false });
    }
  },

  fetchProviders: async () => {
    set({ loading: true, error: null });
    try {
      const response = await invoke<ApiResponse<Provider[]>>('list_providers_simple');
      if (response.success && response.data) {
        set({ providers: response.data, loading: false });
      } else {
        set({ error: response.error || 'Failed to fetch providers', loading: false });
      }
    } catch (error) {
      set({ error: `Failed to fetch providers: ${error}`, loading: false });
    }
  },

  addProvider: async (name: string, provider_type: string, model: string) => {
    set({ loading: true, error: null });
    try {
      const response = await invoke<ApiResponse<Provider>>('add_provider_simple', {
        request: { name, provider_type, model }
      });
      
      if (response.success && response.data) {
        const { providers } = get();
        set({ 
          providers: [response.data, ...providers], 
          loading: false 
        });
      } else {
        set({ error: response.error || 'Failed to add provider', loading: false });
      }
    } catch (error) {
      set({ error: `Failed to add provider: ${error}`, loading: false });
    }
  },

  clearError: () => set({ error: null }),
}));