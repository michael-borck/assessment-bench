import React from 'react'
import { FileText, Plus, Trash2, Download, Upload, Eye, CheckCircle } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { useToast } from '../hooks/useToast'
import { cn } from '../lib/utils'
import type { TemplateCategory, RubricTemplate } from '../types/templates'
import { TEMPLATE_CATEGORIES } from '../data/built-in-templates'

export function TemplateLibrary() {
  const {
    getAllTemplates,
    getTemplatesByCategory,
    saveCustomTemplate,
    deleteCustomTemplate,
    setSelectedTemplate,
    loadTemplateAsRubric,
    selectedTemplate
  } = useAppStore()
  
  const [selectedCategory, setSelectedCategory] = React.useState<TemplateCategory>('essays')
  const [previewTemplate, setPreviewTemplate] = React.useState<RubricTemplate | null>(null)
  const toast = useToast()

  const templates = getTemplatesByCategory(selectedCategory)
  const allTemplates = getAllTemplates()

  const handleUseTemplate = (template: RubricTemplate) => {
    loadTemplateAsRubric(template.id)
    setSelectedTemplate(template.id)
    toast.success(`Loaded template: ${template.name}`)
  }

  const handleDeleteCustomTemplate = (templateId: string) => {
    const template = allTemplates.find(t => t.id === templateId)
    if (template?.createdBy === 'user') {
      deleteCustomTemplate(templateId)
      toast.success(`Deleted template: ${template.name}`)
    }
  }

  const handleExportTemplate = (template: RubricTemplate) => {
    const exportData = {
      template,
      exportedAt: new Date().toISOString(),
      version: '1.0'
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${template.name.replace(/\s+/g, '-').toLowerCase()}-template.json`
    a.click()
    URL.revokeObjectURL(url)
    
    toast.success(`Exported template: ${template.name}`)
  }

  const handleImportTemplate = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        try {
          const text = await file.text()
          const importData = JSON.parse(text)
          
          if (importData.template && importData.template.criteria) {
            const { template } = importData
            // Remove system-specific fields to avoid conflicts
            const { id, createdAt, createdBy, ...templateData } = template
            
            saveCustomTemplate({
              ...templateData,
              category: 'custom' as TemplateCategory,
              tags: [...(templateData.tags || []), 'imported']
            })
            
            toast.success(`Imported template: ${template.name}`)
          } else {
            toast.error('Invalid template file format')
          }
        } catch (error) {
          console.error('Import error:', error)
          toast.error('Failed to import template')
        }
      }
    }
    input.click()
  }

  return (
    <div className="flex h-full gap-6">
      {/* Category Sidebar */}
      <div className="w-64 border-r pr-4">
        <div className="mb-4">
          <h2 className="text-lg font-semibold mb-2">Template Categories</h2>
          <button
            onClick={handleImportTemplate}
            className="flex items-center gap-2 w-full rounded-md border border-dashed border-gray-300 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50"
          >
            <Upload className="h-4 w-4" />
            Import Template
          </button>
        </div>
        
        <div className="space-y-2">
          {Object.entries(TEMPLATE_CATEGORIES).map(([key, category]) => {
            const count = getTemplatesByCategory(key as TemplateCategory).length
            const isActive = selectedCategory === key
            
            return (
              <button
                key={key}
                onClick={() => setSelectedCategory(key as TemplateCategory)}
                className={cn(
                  "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span>{category.name}</span>
                </div>
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full",
                  isActive ? "bg-primary-foreground/20" : "bg-muted"
                )}>
                  {count}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Template Grid */}
      <div className="flex-1 min-w-0">
        <div className="mb-4">
          <h2 className="text-lg font-semibold">
            {TEMPLATE_CATEGORIES[selectedCategory].name}
          </h2>
          <p className="text-sm text-muted-foreground">
            {TEMPLATE_CATEGORIES[selectedCategory].description}
          </p>
        </div>

        {templates.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No templates in this category</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {templates.map((template) => (
              <div
                key={template.id}
                className={cn(
                  "rounded-lg border p-4 transition-colors hover:shadow-md",
                  selectedTemplate === template.id
                    ? "border-primary bg-primary/5"
                    : "border-border bg-card"
                )}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-medium text-sm">{template.name}</h3>
                    <p className="text-xs text-muted-foreground mt-1">
                      {template.description}
                    </p>
                  </div>
                  {selectedTemplate === template.id && (
                    <CheckCircle className="h-4 w-4 text-primary" />
                  )}
                </div>

                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
                  <span>{template.criteria.length} criteria</span>
                  <span>•</span>
                  <span>{template.totalPoints} points</span>
                  <span>•</span>
                  <span>{template.createdBy === 'system' ? 'Built-in' : 'Custom'}</span>
                </div>

                <div className="flex flex-wrap gap-1 mb-3">
                  {template.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 text-xs bg-muted text-muted-foreground rounded"
                    >
                      {tag}
                    </span>
                  ))}
                  {template.tags.length > 3 && (
                    <span className="px-2 py-0.5 text-xs bg-muted text-muted-foreground rounded">
                      +{template.tags.length - 3} more
                    </span>
                  )}
                </div>

                <div className="flex gap-1">
                  <button
                    onClick={() => handleUseTemplate(template)}
                    className="flex-1 flex items-center justify-center gap-1 rounded px-2 py-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    <Plus className="h-3 w-3" />
                    Use Template
                  </button>
                  <button
                    onClick={() => setPreviewTemplate(template)}
                    className="rounded p-1 hover:bg-accent"
                    title="Preview template"
                  >
                    <Eye className="h-3 w-3" />
                  </button>
                  <button
                    onClick={() => handleExportTemplate(template)}
                    className="rounded p-1 hover:bg-accent"
                    title="Export template"
                  >
                    <Download className="h-3 w-3" />
                  </button>
                  {template.createdBy === 'user' && (
                    <button
                      onClick={() => handleDeleteCustomTemplate(template.id)}
                      className="rounded p-1 hover:bg-destructive/20"
                      title="Delete template"
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Template Preview Modal */}
      {previewTemplate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">{previewTemplate.name}</h2>
                <button
                  onClick={() => setPreviewTemplate(null)}
                  className="rounded p-1 hover:bg-accent"
                >
                  ×
                </button>
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                {previewTemplate.description}
              </p>
            </div>
            
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Total Points:</span> {previewTemplate.totalPoints}
                </div>
                <div>
                  <span className="font-medium">Criteria:</span> {previewTemplate.criteria.length}
                </div>
                <div>
                  <span className="font-medium">Category:</span> {TEMPLATE_CATEGORIES[previewTemplate.category].name}
                </div>
                <div>
                  <span className="font-medium">Type:</span> {previewTemplate.createdBy === 'system' ? 'Built-in' : 'Custom'}
                </div>
              </div>

              <div>
                <h3 className="font-medium mb-2">Grading Criteria</h3>
                <div className="space-y-3">
                  {previewTemplate.criteria.map((criterion) => (
                    <div key={criterion.id} className="border rounded p-3">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-sm">{criterion.name}</h4>
                        <span className="text-xs bg-muted px-2 py-1 rounded">
                          {criterion.maxPoints} pts
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">
                        {criterion.description}
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        {criterion.performanceLevels.map((level) => (
                          <div key={level.level} className="flex justify-between">
                            <span>{level.level}:</span>
                            <span>{level.points} pts</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}