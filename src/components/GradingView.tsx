import React from 'react'
import { Play, Edit3, Loader2 } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { tauriApi } from '../lib/tauri'
import { useToast } from '../hooks/useToast'
import { cn } from '../lib/utils'
import { PromptEditor } from './PromptEditor'

export function GradingView() {
  const { 
    files,
    currentFile,
    selectedFiles,
    currentProvider,
    providers 
  } = useAppStore()

  const [fileContent, setFileContent] = React.useState<string>('')
  const [isLoadingContent, setIsLoadingContent] = React.useState(false)
  const [showPromptEditor, setShowPromptEditor] = React.useState(false)
  const toast = useToast()

  const currentProviderConfig = providers[currentProvider]
  const isProviderConfigured = !!currentProviderConfig.apiKey

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

  return (
    <div className="flex h-full flex-col p-6">
      {/* Document Preview */}
      <div className="flex-1 rounded-lg border bg-card p-6 mb-4">
        {currentFile ? (
          <div className="h-full flex flex-col">
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
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <p className="text-lg mb-2">No document selected</p>
              <p className="text-sm">Select a file from the sidebar to preview</p>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={() => setShowPromptEditor(true)}
          className="flex items-center gap-2 rounded-md border border-input px-4 py-2 text-sm font-medium hover:bg-accent"
        >
          <Edit3 className="h-4 w-4" />
          Edit Prompts
        </button>
        <button 
          disabled={!currentFile || !isProviderConfigured}
          className={cn(
            "flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors",
            currentFile && isProviderConfigured
              ? "bg-primary text-primary-foreground hover:bg-primary/90"
              : "bg-muted text-muted-foreground cursor-not-allowed"
          )}
        >
          <Play className="h-4 w-4" />
          Grade Selected
        </button>
        <button 
          disabled={selectedFiles.length === 0 || !isProviderConfigured}
          className={cn(
            "flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors",
            selectedFiles.length > 0 && isProviderConfigured
              ? "border-input hover:bg-accent"
              : "border-muted text-muted-foreground cursor-not-allowed"
          )}
        >
          <Play className="h-4 w-4" />
          Grade All ({selectedFiles.length})
        </button>
      </div>
    </div>
  )
}