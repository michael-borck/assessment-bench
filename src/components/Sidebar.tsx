import React from 'react'
import { FileText, Settings, History, Zap, Upload, Trash2, ChevronRight, ChevronDown, Circle } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { cn } from '../lib/utils'
import { tauriApi, type FileInfo } from '../lib/tauri'
import { useToast } from '../hooks/useToast'

export function Sidebar() {
  const { 
    sidebarOpen, 
    currentView, 
    setCurrentView,
    files,
    setFiles,
    selectedFiles,
    setSelectedFiles,
    currentFile,
    setCurrentFile,
    currentProvider,
    providers
  } = useAppStore()
  
  const [isLoading, setIsLoading] = React.useState(false)
  const [submissionsExpanded, setSubmissionsExpanded] = React.useState(true)
  const toast = useToast()
  
  const isProviderConfigured = !!providers[currentProvider].apiKey

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
      if (process.env.NODE_ENV === 'development') {
        console.error('Error browsing files:', error)
      }
      toast.error('Failed to browse files', 'Please check folder permissions and try again')
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleRemoveFile = (fileName: string) => {
    setFiles(files.filter(f => f.name !== fileName))
    setSelectedFiles(selectedFiles.filter(f => f !== fileName))
    if (currentFile === fileName) {
      setCurrentFile(null)
    }
    toast.success(`Removed ${fileName}`)
  }
  
  const handleFileClick = (file: FileInfo) => {
    setCurrentFile(file.name)
    if (currentView !== 'grading') {
      setCurrentView('grading')
    }
  }

  const menuItems = [
    {
      key: 'settings' as const,
      label: 'Provider Settings',
      icon: Settings,
    },
    {
      key: 'history' as const,
      label: 'Grading History',
      icon: History,
    },
  ]

  return (
    <div className="flex h-full flex-col bg-sidebar">
      {/* Logo/Brand */}
      <div className="border-b p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Zap className="h-4 w-4" />
          </div>
          {sidebarOpen && (
            <span className="text-sm font-semibold">AI Assessor</span>
          )}
        </div>
      </div>

      {/* Submissions Tree */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="p-2">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSubmissionsExpanded(!submissionsExpanded)}
              className="flex flex-1 items-center gap-2 rounded-lg px-3 py-2 text-left text-sm font-medium hover:bg-accent"
            >
              {submissionsExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
              <FileText className="h-4 w-4" />
              {sidebarOpen && (
                <span className="flex-1">
                  Submissions {files.length > 0 && `(${files.length})`}
                </span>
              )}
            </button>
            {sidebarOpen && (
              <button
                onClick={handleBrowseFiles}
                disabled={isLoading}
                className="rounded-md p-1.5 hover:bg-accent"
                title="Browse for files"
              >
                <Upload className="h-4 w-4" />
              </button>
            )}
          </div>
          
          {/* File List */}
          {sidebarOpen && submissionsExpanded && (
            <div className="mt-2 space-y-1 pl-4">
              {files.length === 0 ? (
                <div className="py-2 text-xs text-muted-foreground pl-6">
                  No files loaded. Click upload to browse.
                </div>
              ) : (
                files.map((file) => (
                  <div
                    key={file.path}
                    className={cn(
                      "flex items-center gap-2 rounded-md px-2 py-1.5 text-xs hover:bg-accent group",
                      currentFile === file.name && "bg-accent"
                    )}
                  >
                    <button
                      onClick={() => handleFileClick(file)}
                      className="flex flex-1 items-center gap-2 text-left"
                    >
                      <FileText className="h-3 w-3" />
                      <span className="truncate">{file.name}</span>
                    </button>
                    <button
                      onClick={() => handleRemoveFile(file.name)}
                      className="opacity-0 group-hover:opacity-100 rounded p-0.5 hover:bg-destructive/20"
                      title="Remove file"
                    >
                      <Trash2 className="h-3 w-3 text-destructive" />
                    </button>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Other Navigation Items */}
        <nav className="p-2 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = currentView === item.key
            
            return (
              <button
                key={item.key}
                onClick={() => setCurrentView(item.key)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {sidebarOpen && <span>{item.label}</span>}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Provider Status at Bottom */}
      {sidebarOpen && (
        <div className="border-t p-4">
          <div className="flex items-center gap-2 text-xs">
            <Circle className={cn(
              "h-2 w-2 fill-current",
              isProviderConfigured ? "text-green-500" : "text-red-500"
            )} />
            <span className="text-muted-foreground">Provider:</span>
            <span className="font-medium capitalize">{currentProvider}</span>
          </div>
          {!isProviderConfigured && (
            <button
              onClick={() => setCurrentView('settings')}
              className="mt-2 text-xs text-primary hover:underline"
            >
              Configure API Key →
            </button>
          )}
        </div>
      )}
    </div>
  )
}