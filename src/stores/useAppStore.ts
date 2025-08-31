import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type LLMProvider = 'openai' | 'anthropic' | 'groq' | 'gemini' | 'ollama' | 'openrouter'

interface ProviderConfig {
  type: LLMProvider
  apiKey?: string
  baseUrl?: string
  bearerToken?: string
  model?: string
  temperature?: number
}

interface AppState {
  // UI State
  sidebarOpen: boolean
  currentView: 'grading' | 'settings' | 'history'
  
  // Provider Configuration
  currentProvider: LLMProvider
  providers: Record<LLMProvider, ProviderConfig>
  
  // Prompts
  systemPrompt: string
  userPrompt: string
  
  // Files
  selectedFiles: string[]
  currentFile: string | null
  
  // Actions
  setSidebarOpen: (open: boolean) => void
  setCurrentView: (view: 'grading' | 'settings' | 'history') => void
  setCurrentProvider: (provider: LLMProvider) => void
  updateProviderConfig: (provider: LLMProvider, config: Partial<ProviderConfig>) => void
  setSystemPrompt: (prompt: string) => void
  setUserPrompt: (prompt: string) => void
  setSelectedFiles: (files: string[]) => void
  setCurrentFile: (file: string | null) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial UI State
      sidebarOpen: true,
      currentView: 'grading',
      
      // Initial Provider Configuration
      currentProvider: 'openai',
      providers: {
        openai: { type: 'openai', model: 'gpt-4-turbo', temperature: 0.7 },
        anthropic: { type: 'anthropic', model: 'claude-3-opus-20240229', temperature: 0.7 },
        groq: { type: 'groq', model: 'llama-3.1-70b-versatile', temperature: 0.7 },
        gemini: { type: 'gemini', model: 'gemini-1.5-pro', temperature: 0.7 },
        ollama: { type: 'ollama', baseUrl: 'http://localhost:11434', model: 'llama3', temperature: 0.7 },
        openrouter: { type: 'openrouter', model: 'openai/gpt-4-turbo', temperature: 0.7 },
      },
      
      // Initial Prompts
      systemPrompt: '',
      userPrompt: '',
      
      // Initial Files
      selectedFiles: [],
      currentFile: null,
      
      // Actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setCurrentView: (view) => set({ currentView: view }),
      setCurrentProvider: (provider) => set({ currentProvider: provider }),
      updateProviderConfig: (provider, config) =>
        set((state) => ({
          providers: {
            ...state.providers,
            [provider]: { ...state.providers[provider], ...config },
          },
        })),
      setSystemPrompt: (prompt) => set({ systemPrompt: prompt }),
      setUserPrompt: (prompt) => set({ userPrompt: prompt }),
      setSelectedFiles: (files) => set({ selectedFiles: files }),
      setCurrentFile: (file) => set({ currentFile: file }),
    }),
    {
      name: 'ai-assessor-storage',
      partialize: (state) => ({
        currentProvider: state.currentProvider,
        providers: state.providers,
        systemPrompt: state.systemPrompt,
        userPrompt: state.userPrompt,
      }),
    }
  )
)