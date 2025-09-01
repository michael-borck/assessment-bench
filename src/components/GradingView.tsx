import React from 'react'
import { Play, Edit3, Loader2, FileText, Brain, Zap } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { tauriApi } from '../lib/tauri'
import { useToast } from '../hooks/useToast'
import { cn } from '../lib/utils'
import { PromptEditor } from './PromptEditor'
import { SupportFileManager } from './SupportFileManager'
import { WorkflowSelector } from './WorkflowSelector'
import { DocumentAnalysisPreview } from './DocumentAnalysisPreview'

export function GradingView() {
  const { 
    files,
    currentFile,
    selectedFiles,
    currentProvider,
    currentWorkflow,
    providers,
    supportFiles
  } = useAppStore()

  const [fileContent, setFileContent] = React.useState<string>('')
  const [isLoadingContent, setIsLoadingContent] = React.useState(false)
  const [showPromptEditor, setShowPromptEditor] = React.useState(false)
  const [showSupportFiles, setShowSupportFiles] = React.useState(false)
  const [showWorkflowSelector, setShowWorkflowSelector] = React.useState(false)
  const toast = useToast()

  const currentProviderConfig = providers[currentProvider]
  const isProviderConfigured = !!currentProviderConfig.apiKey
  
  // Check if all required support files are loaded
  const requiredSupportFiles = ['rubric', 'markingGuide', 'guidelines'] as const
  const allSupportFilesLoaded = requiredSupportFiles.every(key => supportFiles[key]?.loaded)
  
  // Check if assignment specification is available (optional but enhances grading)
  const hasAssignmentSpec = supportFiles.assignmentSpec?.loaded

  React.useEffect(() => {
    if (currentFile) {
      loadFileContent(currentFile)
    }
  }, [currentFile])

  const loadFileContent = async (fileName: string) => {
    setIsLoadingContent(true)
    try {
      // Find the file path from the files array
      const file = files.find(f => f.name === fileName)
      if (!file) {
        throw new Error('File not found in list')
      }
      const content = await tauriApi.readFileContent(file.path)
      setFileContent(content)
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error reading file:', error)
      }
      toast.error('Failed to read file', `Could not load ${fileName}`)
      setFileContent('Error loading file content')
    } finally {
      setIsLoadingContent(false)
    }
  }

  if (showPromptEditor) {
    return (
      <div className="h-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Prompt Editor</h1>
          <button
            onClick={() => setShowPromptEditor(false)}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
          >
            Back to Grading
          </button>
        </div>
        <PromptEditor />
      </div>
    )
  }

  if (showSupportFiles) {
    return (
      <div className="h-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Support Files</h1>
          <button
            onClick={() => setShowSupportFiles(false)}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
          >
            Back to Grading
          </button>
        </div>
        <SupportFileManager />
      </div>
    )
  }

  if (showWorkflowSelector) {
    return (
      <div className="h-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Grading Workflow</h1>
          <button
            onClick={() => setShowWorkflowSelector(false)}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
          >
            Back to Grading
          </button>
        </div>
        <WorkflowSelector />
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col p-6">
      {/* Document Preview */}
      <div className="flex-1 rounded-lg border bg-card p-6 mb-4">
        {currentFile ? (
          <div className="h-full flex">
            {/* Document Content */}
            <div className="flex-1 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold">Document Preview</h2>
                  <p className="text-sm text-muted-foreground mt-1">{currentFile}</p>
                </div>
              </div>
              
              <div className="flex-1 rounded-lg bg-muted/50 p-4 overflow-auto">
                {isLoadingContent ? (
                  <div className="flex items-center justify-center h-32">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </div>
                ) : (
                  <pre className="text-sm whitespace-pre-wrap font-mono">{fileContent || "No content available"}</pre>
                )}
              </div>
            </div>
            
            {/* Enhanced Analysis Panel */}
            {currentWorkflow === 'enhanced' && fileContent && (
              <div className="w-80 ml-4 border-l pl-4">
                <div className="h-full overflow-auto">
                  <DocumentAnalysisPreview content={fileContent} />
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <p className="text-lg mb-2">No document selected</p>
              <p className="text-sm">Select a file from the sidebar to preview</p>
              {currentWorkflow === 'enhanced' && (
                <p className="text-xs text-blue-600 mt-2">Enhanced workflow will provide document analysis</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => setShowWorkflowSelector(true)}
          className={cn(
            "flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors",
            currentWorkflow === 'enhanced'
              ? "border-blue-300 bg-blue-50 text-blue-700 hover:bg-blue-100"
              : "border-gray-300 bg-gray-50 text-gray-700 hover:bg-gray-100"
          )}
        >
          {currentWorkflow === 'enhanced' ? (
            <Brain className="h-4 w-4" />
          ) : (
            <Zap className="h-4 w-4" />
          )}
          {currentWorkflow === 'enhanced' ? 'Enhanced' : 'Basic'} Workflow
        </button>
        <button
          onClick={() => setShowSupportFiles(true)}
          className={cn(
            "flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors",
            allSupportFilesLoaded 
              ? "border-green-300 bg-green-50 text-green-700 hover:bg-green-100"
              : "border-orange-300 bg-orange-50 text-orange-700 hover:bg-orange-100"
          )}
        >
          <FileText className="h-4 w-4" />
          Support Files {allSupportFilesLoaded ? '✓' : '!'}
          {hasAssignmentSpec && <span className="text-xs bg-blue-100 text-blue-800 px-1 rounded">+Spec</span>}
        </button>
        <button
          onClick={() => setShowPromptEditor(true)}
          className="flex items-center gap-2 rounded-md border border-input px-4 py-2 text-sm font-medium hover:bg-accent"
        >
          <Edit3 className="h-4 w-4" />
          Edit Prompts
        </button>
        <button 
          disabled={!currentFile || !isProviderConfigured || !allSupportFilesLoaded}
          className={cn(
            "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            currentFile && isProviderConfigured && allSupportFilesLoaded
              ? "bg-primary text-primary-foreground hover:bg-primary/90"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          )}
          title={!allSupportFilesLoaded ? "Load all support files first" : undefined}
        >
          <Play className="h-4 w-4" />
          Grade Selected
        </button>
        <button 
          disabled={selectedFiles.length === 0 || !isProviderConfigured || !allSupportFilesLoaded}
          className={cn(
            "flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors",
            selectedFiles.length > 0 && isProviderConfigured && allSupportFilesLoaded
              ? "border-input hover:bg-accent"
              : "border-muted text-muted-foreground cursor-not-allowed"
          )}
          title={!allSupportFilesLoaded ? "Load all support files first" : undefined}
        >
          <Play className="h-4 w-4" />
          Grade All ({selectedFiles.length})
        </button>
      </div>
    </div>
  )
}