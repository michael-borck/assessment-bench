import React from 'react'
import { FileText, Upload, Play, Settings as SettingsIcon, Loader2 } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { tauriApi, type FileInfo } from '../lib/tauri'
import { useToast } from '../hooks/useToast'
import { cn } from '../lib/utils'

export function GradingView() {
  const { 
    currentFile, 
    setCurrentFile,
    setSelectedFiles,
    currentProvider,
    providers 
  } = useAppStore()

  const [files, setFiles] = React.useState<FileInfo[]>([])
  const [fileContent, setFileContent] = React.useState<string>('')
  const [isLoading, setIsLoading] = React.useState(false)
  const [isLoadingContent, setIsLoadingContent] = React.useState(false)
  const toast = useToast()

  const currentProviderConfig = providers[currentProvider]
  const isProviderConfigured = !!currentProviderConfig.apiKey

  const handleBrowseFiles = async () => {
    setIsLoading(true)
    try {
      const result = await tauriApi.browseFolder()
      setFiles(result)
      setSelectedFiles(result.map(f => f.name))
      if (result.length > 0) {
        toast.success(`Loaded ${result.length} files`)
      }
    } catch (error) {
      // Log to console in development, show user-friendly message in production
      if (process.env.NODE_ENV === 'development') {
        console.error('Error browsing files:', error)
      }
      toast.error('Failed to browse files', 'Please check folder permissions and try again')
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileSelect = async (file: FileInfo) => {
    setCurrentFile(file.name)
    setIsLoadingContent(true)
    try {
      const content = await tauriApi.readFileContent(file.path)
      setFileContent(content)
    } catch (error) {
      // Log to console in development, show user-friendly message in production
      if (process.env.NODE_ENV === 'development') {
        console.error('Error reading file:', error)
      }
      toast.error('Failed to read file', `Could not load ${file.name}`)
      setFileContent('Error loading file content')
    } finally {
      setIsLoadingContent(false)
    }
  }

  React.useEffect(() => {
    // Load files on component mount
    handleBrowseFiles()
  }, [])

  return (
    <div className="flex h-full gap-6">
      {/* Left Panel - File Browser */}
      <div className="w-1/3 min-w-0">
        <div className="rounded-lg border bg-card p-4 h-full">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Submissions</h2>
            <button 
              onClick={handleBrowseFiles}
              disabled={isLoading}
              className="rounded-md p-2 hover:bg-accent disabled:opacity-50"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
            </button>
          </div>
          
          {files.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground mb-2">No submissions loaded</p>
              <button 
                onClick={handleBrowseFiles}
                disabled={isLoading}
                className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Upload className="h-4 w-4" />
                )}
                Browse Files
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              {files.map((file) => (
                <button
                  key={file.path}
                  onClick={() => handleFileSelect(file)}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors hover:bg-accent",
                    currentFile === file.name ? "border-primary bg-accent" : "border-border"
                  )}
                >
                  <FileText className="h-4 w-4 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="truncate text-sm font-medium">{file.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {(file.size / 1024).toFixed(1)} KB
                      {file.modified && ` • ${new Date(file.modified).toLocaleDateString()}`}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Panel - Content and Actions */}
      <div className="flex-1 min-w-0">
        <div className="space-y-4">
          {/* Provider Status */}
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "h-3 w-3 rounded-full",
                  isProviderConfigured ? "bg-green-500" : "bg-red-500"
                )} />
                <div>
                  <p className="font-medium capitalize">{currentProvider}</p>
                  <p className="text-sm text-muted-foreground">
                    {isProviderConfigured ? 'Connected' : 'Not configured'}
                  </p>
                </div>
              </div>
              <button 
                onClick={() => {/* TODO: Open settings */}}
                className="rounded-md p-2 hover:bg-accent"
              >
                <SettingsIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Document Preview */}
          <div className="rounded-lg border bg-card p-4 flex-1">
            <h3 className="text-lg font-semibold mb-4">Document Preview</h3>
            {currentFile ? (
              <div className="space-y-4">
                <div className="rounded-lg bg-muted p-4">
                  <p className="text-sm text-muted-foreground mb-2">Selected file:</p>
                  <p className="font-medium">{currentFile}</p>
                </div>
                <div className="rounded-lg bg-muted/50 p-4 min-h-64 max-h-96 overflow-auto">
                  {isLoadingContent ? (
                    <div className="flex items-center justify-center h-32">
                      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                  ) : (
                    <pre className="text-sm whitespace-pre-wrap">{fileContent || "No content available"}</pre>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-muted-foreground">
                <div className="text-center">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select a submission to preview</p>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
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
              disabled={files.length === 0 || !isProviderConfigured}
              className={cn(
                "flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors",
                files.length > 0 && isProviderConfigured
                  ? "border-input hover:bg-accent"
                  : "border-muted text-muted-foreground cursor-not-allowed"
              )}
            >
              <Play className="h-4 w-4" />
              Grade All ({files.length})
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}