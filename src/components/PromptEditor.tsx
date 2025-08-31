import React from 'react'
import { Save, Copy, Download, Upload, FileText } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { useToast } from '../hooks/useToast'
import { cn } from '../lib/utils'

interface PromptTemplate {
  name: string
  systemPrompt: string
  userPrompt: string
}

// Predefined templates for common grading scenarios
const templates: PromptTemplate[] = [
  {
    name: 'Essay Grading',
    systemPrompt: `You are an experienced academic evaluator. Grade the submitted essay based on:
1. Thesis clarity and argumentation
2. Evidence and supporting details
3. Organization and structure
4. Writing quality and grammar
5. Originality and critical thinking

Provide detailed feedback with specific examples from the text.`,
    userPrompt: 'Grade this essay submission according to the rubric provided. Be constructive and specific in your feedback.',
  },
  {
    name: 'Code Assignment',
    systemPrompt: `You are a programming instructor evaluating code submissions. Assess based on:
1. Correctness and functionality
2. Code quality and style
3. Efficiency and optimization
4. Documentation and comments
5. Error handling

Provide line-specific feedback where applicable.`,
    userPrompt: 'Review this code submission for correctness, style, and best practices. Highlight both strengths and areas for improvement.',
  },
  {
    name: 'Research Paper',
    systemPrompt: `You are an academic reviewer evaluating research papers. Consider:
1. Research question and hypothesis
2. Methodology and approach
3. Data analysis and interpretation
4. Literature review quality
5. Conclusions and implications

Provide scholarly feedback appropriate for academic work.`,
    userPrompt: 'Evaluate this research paper according to academic standards. Focus on methodology, analysis, and contribution to the field.',
  },
]

export function PromptEditor() {
  const { systemPrompt, userPrompt, setSystemPrompt, setUserPrompt } = useAppStore()
  const toast = useToast()
  const [selectedTemplate, setSelectedTemplate] = React.useState<string>('')

  const handleTemplateSelect = (template: PromptTemplate) => {
    setSystemPrompt(template.systemPrompt)
    setUserPrompt(template.userPrompt)
    setSelectedTemplate(template.name)
    toast.success(`Loaded template: ${template.name}`)
  }

  const handleSavePrompts = () => {
    // Save prompts to local storage
    const prompts = { systemPrompt, userPrompt, savedAt: new Date().toISOString() }
    localStorage.setItem('ai-assessor-prompts', JSON.stringify(prompts))
    toast.success('Prompts saved locally')
  }

  const handleLoadPrompts = () => {
    const saved = localStorage.getItem('ai-assessor-prompts')
    if (saved) {
      const prompts = JSON.parse(saved)
      setSystemPrompt(prompts.systemPrompt)
      setUserPrompt(prompts.userPrompt)
      toast.success('Prompts loaded from local storage')
    } else {
      toast.error('No saved prompts found')
    }
  }

  const handleExportPrompts = () => {
    const prompts = {
      systemPrompt,
      userPrompt,
      exportedAt: new Date().toISOString()
    }
    const blob = new Blob([JSON.stringify(prompts, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `prompts-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Prompts exported')
  }

  const handleImportPrompts = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        try {
          const text = await file.text()
          const prompts = JSON.parse(text)
          if (prompts.systemPrompt && prompts.userPrompt) {
            setSystemPrompt(prompts.systemPrompt)
            setUserPrompt(prompts.userPrompt)
            toast.success('Prompts imported successfully')
          } else {
            toast.error('Invalid prompt file format')
          }
        } catch {
          toast.error('Failed to import prompts')
        }
      }
    }
    input.click()
  }

  const handleCopyPrompt = (prompt: string, type: 'system' | 'user') => {
    navigator.clipboard.writeText(prompt)
    toast.success(`${type === 'system' ? 'System' : 'User'} prompt copied to clipboard`)
  }

  return (
    <div className="flex h-full gap-6">
      {/* Left Panel - Templates */}
      <div className="w-1/3 min-w-0">
        <div className="rounded-lg border bg-card p-4 h-full">
          <h2 className="text-lg font-semibold mb-4">Prompt Templates</h2>
          
          <div className="space-y-2 mb-4">
            {templates.map((template) => (
              <button
                key={template.name}
                onClick={() => handleTemplateSelect(template)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-accent",
                  selectedTemplate === template.name ? "border-primary bg-accent" : "border-border"
                )}
              >
                <FileText className="h-4 w-4 flex-shrink-0" />
                <span className="font-medium">{template.name}</span>
              </button>
            ))}
          </div>

          <div className="border-t pt-4 space-y-2">
            <button
              onClick={handleSavePrompts}
              className="flex w-full items-center gap-2 rounded-md border border-input px-3 py-2 text-sm hover:bg-accent"
            >
              <Save className="h-4 w-4" />
              Save Current Prompts
            </button>
            <button
              onClick={handleLoadPrompts}
              className="flex w-full items-center gap-2 rounded-md border border-input px-3 py-2 text-sm hover:bg-accent"
            >
              <Upload className="h-4 w-4" />
              Load Saved Prompts
            </button>
            <button
              onClick={handleExportPrompts}
              className="flex w-full items-center gap-2 rounded-md border border-input px-3 py-2 text-sm hover:bg-accent"
            >
              <Download className="h-4 w-4" />
              Export Prompts
            </button>
            <button
              onClick={handleImportPrompts}
              className="flex w-full items-center gap-2 rounded-md border border-input px-3 py-2 text-sm hover:bg-accent"
            >
              <Upload className="h-4 w-4" />
              Import Prompts
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel - Prompt Editors */}
      <div className="flex-1 min-w-0 space-y-4">
        {/* System Prompt */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold">System Prompt</h3>
            <button
              onClick={() => handleCopyPrompt(systemPrompt, 'system')}
              className="rounded-md p-2 hover:bg-accent"
              title="Copy to clipboard"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-muted-foreground mb-3">
            Define the AI's role, grading criteria, and evaluation framework
          </p>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="Enter the system prompt that defines how the AI should grade submissions..."
            className="w-full h-48 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none font-mono"
          />
          <div className="mt-2 text-xs text-muted-foreground">
            {systemPrompt.length} characters
          </div>
        </div>

        {/* User Prompt */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold">User Prompt</h3>
            <button
              onClick={() => handleCopyPrompt(userPrompt, 'user')}
              className="rounded-md p-2 hover:bg-accent"
              title="Copy to clipboard"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
          <p className="text-sm text-muted-foreground mb-3">
            Provide specific instructions for this grading session
          </p>
          <textarea
            value={userPrompt}
            onChange={(e) => setUserPrompt(e.target.value)}
            placeholder="Enter specific instructions for grading these submissions..."
            className="w-full h-48 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none font-mono"
          />
          <div className="mt-2 text-xs text-muted-foreground">
            {userPrompt.length} characters
          </div>
        </div>

        {/* Tips */}
        <div className="rounded-lg border bg-muted/50 p-4">
          <h4 className="font-medium mb-2">Tips for Effective Prompts</h4>
          <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
            <li>Be specific about grading criteria and point distribution</li>
            <li>Include rubric details in the system prompt</li>
            <li>Specify the tone and style of feedback (constructive, formal, etc.)</li>
            <li>Mention any specific areas to focus on or ignore</li>
            <li>Consider including example feedback for consistency</li>
          </ul>
        </div>
      </div>
    </div>
  )
}