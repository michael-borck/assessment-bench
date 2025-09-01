import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { FileInfo } from '../lib/tauri'
import type { RubricTemplate, TemplateCategory } from '../types/templates'
import { BUILT_IN_TEMPLATES } from '../data/built-in-templates'

export type LLMProvider = 'openai' | 'anthropic' | 'groq' | 'gemini' | 'ollama' | 'openrouter'

interface ProviderConfig {
  type: LLMProvider
  apiKey?: string
  baseUrl?: string
  bearerToken?: string
  model: string
  temperature: number
}

export interface SupportFile {
  name: string
  path: string
  content: string
  type: 'rubric' | 'marking_guide' | 'guidelines' | 'assignment_spec'
  loaded: boolean
}

export interface SupportFiles {
  rubric?: SupportFile
  markingGuide?: SupportFile
  guidelines?: SupportFile
  assignmentSpec?: SupportFile
}

export type WorkflowType = 'basic' | 'enhanced'

interface DocumentAnalysisConfig {
  baseUrl: string
  apiKey?: string
  enabled: boolean
}

interface AppState {
  // UI State
  sidebarOpen: boolean
  currentView: 'grading' | 'settings' | 'history'
  
  // Workflow Configuration
  currentWorkflow: WorkflowType
  
  // Document Analysis Configuration
  documentAnalysisConfig: DocumentAnalysisConfig
  
  // Provider Configuration
  currentProvider: LLMProvider
  providers: Record<LLMProvider, ProviderConfig>
  
  // Prompts
  systemPrompt: string
  userPrompt: string
  
  // Files
  files: FileInfo[]
  selectedFiles: string[]
  currentFile: string | null
  
  // Support Files
  supportFiles: SupportFiles
  
  // Templates
  customTemplates: RubricTemplate[]
  selectedTemplate: string | null
  
  // Actions
  setSidebarOpen: (open: boolean) => void
  setCurrentView: (view: 'grading' | 'settings' | 'history') => void
  setCurrentWorkflow: (workflow: WorkflowType) => void
  updateDocumentAnalysisConfig: (config: Partial<DocumentAnalysisConfig>) => void
  setCurrentProvider: (provider: LLMProvider) => void
  updateProviderConfig: (provider: LLMProvider, config: Partial<ProviderConfig>) => void
  setSystemPrompt: (prompt: string) => void
  setUserPrompt: (prompt: string) => void
  setFiles: (files: FileInfo[]) => void
  setSelectedFiles: (files: string[]) => void
  setCurrentFile: (file: string | null) => void
  setSupportFile: (type: 'rubric' | 'markingGuide' | 'guidelines' | 'assignmentSpec', file: SupportFile) => void
  removeSupportFile: (type: 'rubric' | 'markingGuide' | 'guidelines' | 'assignmentSpec') => void
  clearAllSupportFiles: () => void
  // Template actions
  getAllTemplates: () => RubricTemplate[]
  getTemplatesByCategory: (category: TemplateCategory) => RubricTemplate[]
  getTemplateById: (id: string) => RubricTemplate | null
  saveCustomTemplate: (template: Omit<RubricTemplate, 'id' | 'createdAt' | 'createdBy'>) => void
  deleteCustomTemplate: (id: string) => void
  setSelectedTemplate: (templateId: string | null) => void
  loadTemplateAsRubric: (templateId: string) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Initial UI State
      sidebarOpen: true,
      currentView: 'grading',
      
      // Initial Workflow Configuration
      currentWorkflow: 'basic',
      
      // Initial Document Analysis Configuration
      documentAnalysisConfig: {
        baseUrl: 'http://localhost:8001',
        enabled: true
      },
      
      // Initial Provider Configuration
      currentProvider: 'openai',
      providers: {
        openai: { type: 'openai' as LLMProvider, model: 'gpt-4-turbo', temperature: 0.7 },
        anthropic: { type: 'anthropic' as LLMProvider, model: 'claude-3-opus-20240229', temperature: 0.7 },
        groq: { type: 'groq' as LLMProvider, model: 'llama-3.1-70b-versatile', temperature: 0.7 },
        gemini: { type: 'gemini' as LLMProvider, model: 'gemini-1.5-pro', temperature: 0.7 },
        ollama: { type: 'ollama' as LLMProvider, baseUrl: 'http://localhost:11434', model: 'llama3', temperature: 0.7 },
        openrouter: { type: 'openrouter' as LLMProvider, model: 'openai/gpt-4-turbo', temperature: 0.7 },
      },
      
      // Initial Prompts
      systemPrompt: '',
      userPrompt: '',
      
      // Initial Files
      files: [],
      selectedFiles: [],
      currentFile: null,
      
      // Initial Support Files
      supportFiles: {},
      
      // Initial Templates
      customTemplates: [],
      selectedTemplate: null,
      
      // Actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setCurrentView: (view) => set({ currentView: view }),
      setCurrentWorkflow: (workflow) => set({ currentWorkflow: workflow }),
      updateDocumentAnalysisConfig: (config) =>
        set((state) => ({
          documentAnalysisConfig: { ...state.documentAnalysisConfig, ...config }
        })),
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
      setFiles: (files) => set({ files: files }),
      setSelectedFiles: (files) => set({ selectedFiles: files }),
      setCurrentFile: (file) => set({ currentFile: file }),
      setSupportFile: (type, file) =>
        set((state) => ({
          supportFiles: { ...state.supportFiles, [type]: file },
        })),
      removeSupportFile: (type) =>
        set((state) => {
          const { [type]: removed, ...rest } = state.supportFiles
          return { supportFiles: rest }
        }),
      clearAllSupportFiles: () => set({ supportFiles: {} }),
      
      // Template operations
      getAllTemplates: () => {
        const state = get()
        return [...BUILT_IN_TEMPLATES, ...state.customTemplates]
      },
      
      getTemplatesByCategory: (category: TemplateCategory) => {
        const allTemplates = get().getAllTemplates()
        return allTemplates.filter(template => template.category === category)
      },
      
      getTemplateById: (id: string) => {
        const allTemplates = get().getAllTemplates()
        return allTemplates.find(template => template.id === id) || null
      },
      
      saveCustomTemplate: (templateData: Omit<RubricTemplate, 'id' | 'createdAt' | 'createdBy'>) =>
        set((state) => {
          const newTemplate: RubricTemplate = {
            ...templateData,
            id: `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            createdBy: 'user',
            createdAt: new Date().toISOString(),
          }
          return {
            customTemplates: [...state.customTemplates, newTemplate]
          }
        }),
      
      deleteCustomTemplate: (id: string) =>
        set((state) => ({
          customTemplates: state.customTemplates.filter(template => template.id !== id),
          selectedTemplate: state.selectedTemplate === id ? null : state.selectedTemplate
        })),
      
      setSelectedTemplate: (templateId: string | null) => set({ selectedTemplate: templateId }),
      
      loadTemplateAsRubric: (templateId: string) => {
        const template = get().getTemplateById(templateId)
        if (template) {
          // Convert template to rubric format and set as support file
          const rubricContent = JSON.stringify(template, null, 2)
          const rubricFile: SupportFile = {
            name: `${template.name}.json`,
            path: `template://${templateId}`,
            content: rubricContent,
            type: 'rubric',
            loaded: true
          }
          get().setSupportFile('rubric', rubricFile)
        }
      },
    }),
    {
      name: 'ai-assessor-storage',
      partialize: (state) => ({
        currentProvider: state.currentProvider,
        currentWorkflow: state.currentWorkflow,
        documentAnalysisConfig: state.documentAnalysisConfig,
        providers: state.providers,
        systemPrompt: state.systemPrompt,
        userPrompt: state.userPrompt,
        customTemplates: state.customTemplates,
        selectedTemplate: state.selectedTemplate,
      }),
    }
  )
)