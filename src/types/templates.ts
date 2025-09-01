// Rubric Template System Types

export interface RubricCriterion {
  id: string
  name: string
  description: string
  maxPoints: number
  performanceLevels: PerformanceLevel[]
}

export interface PerformanceLevel {
  level: string // e.g., "Excellent", "Good", "Fair", "Poor"
  description: string
  points: number
}

export interface RubricTemplate {
  id: string
  name: string
  category: TemplateCategory
  description: string
  totalPoints: number
  criteria: RubricCriterion[]
  createdBy: 'system' | 'user'
  createdAt: string
  tags: string[]
}

export type TemplateCategory = 
  | 'essays'
  | 'technical-writing' 
  | 'creative-writing'
  | 'academic-papers'
  | 'code-assignments'
  | 'custom'

export interface TemplateLibrary {
  templates: RubricTemplate[]
  categories: {
    [K in TemplateCategory]: {
      name: string
      description: string
      icon: string
    }
  }
}

// Template operations
export interface TemplateOperations {
  loadTemplate: (templateId: string) => RubricTemplate | null
  saveTemplate: (template: Omit<RubricTemplate, 'id' | 'createdAt'>) => RubricTemplate
  deleteTemplate: (templateId: string) => boolean
  exportTemplates: (templateIds: string[]) => string // JSON string
  importTemplates: (templatesJson: string) => RubricTemplate[]
  searchTemplates: (query: string, category?: TemplateCategory) => RubricTemplate[]
}