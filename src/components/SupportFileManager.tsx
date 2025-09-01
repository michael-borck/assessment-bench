import React from 'react'
import { FileText, Upload, Trash2, CheckCircle, AlertCircle, BookOpen } from 'lucide-react'
import { useAppStore, type SupportFile } from '../stores/useAppStore'
import { tauriApi } from '../lib/tauri'
import { useToast } from '../hooks/useToast'
import { cn } from '../lib/utils'
import { TemplateLibrary } from './TemplateLibrary'
import { AssignmentSpecPreview } from './AssignmentSpecPreview'

export function SupportFileManager() {
  const { 
    supportFiles, 
    setSupportFile, 
    removeSupportFile, 
    clearAllSupportFiles 
  } = useAppStore()
  
  const [isLoading, setIsLoading] = React.useState(false)
  const [showTemplateLibrary, setShowTemplateLibrary] = React.useState(false)
  const toast = useToast()

  const supportFileTypes = [
    {
      key: 'rubric' as const,
      label: 'Report Rubric',
      description: 'Performance descriptions and grading criteria',
      required: true
    },
    {
      key: 'markingGuide' as const,
      label: 'Report Marking Guide',
      description: 'Sub-level marks breakdown for each criterion',
      required: true
    },
    {
      key: 'guidelines' as const,
      label: 'Report Guidelines',
      description: 'Assignment instructions and requirements',
      required: true
    },
    {
      key: 'assignmentSpec' as const,
      label: 'Assignment Specification',
      description: 'Complete assignment document with context and requirements',
      required: false
    }
  ]

  const handleBrowseFiles = async () => {
    setIsLoading(true)
    try {
      const files = await tauriApi.browseSupportFiles()
      
      // Auto-assign files based on filename keywords
      for (const file of files) {
        const fileName = file.name.toLowerCase()
        const content = await tauriApi.readFileContent(file.path)
        
        let type: 'rubric' | 'markingGuide' | 'guidelines' | 'assignmentSpec' | null = null
        
        if (fileName.includes('rubric')) {
          type = 'rubric'
        } else if (fileName.includes('marking') || fileName.includes('guide')) {
          type = 'markingGuide'
        } else if (fileName.includes('guideline') || fileName.includes('instruction')) {
          type = 'guidelines'
        } else if (fileName.includes('assignment') || fileName.includes('spec') || fileName.includes('brief')) {
          type = 'assignmentSpec'
        }
        
        if (type) {
          const supportFile: SupportFile = {
            name: file.name,
            path: file.path,
            content,
            type: type === 'rubric' ? 'rubric' 
                : type === 'markingGuide' ? 'marking_guide' 
                : type === 'guidelines' ? 'guidelines'
                : 'assignment_spec',
            loaded: true
          }
          setSupportFile(type, supportFile)
        }
      }
      
      toast.success(`Loaded ${files.length} support files`)
    } catch (error) {
      console.error('Error loading support files:', error)
      toast.error('Failed to load support files', 'Please check file permissions and try again')
    } finally {
      setIsLoading(false)
    }
  }

  const handleRemoveFile = (type: 'rubric' | 'markingGuide' | 'guidelines' | 'assignmentSpec') => {
    removeSupportFile(type)
    toast.success('Support file removed')
  }

  const handleClearAll = () => {
    clearAllSupportFiles()
    toast.success('All support files cleared')
  }

  const allRequiredLoaded = supportFileTypes
    .filter(type => type.required)
    .every(type => supportFiles[type.key]?.loaded)

  if (showTemplateLibrary) {
    return (
      <div className="h-full flex flex-col">
        <div className="flex items-center justify-between mb-4 pb-4 border-b">
          <h2 className="text-lg font-semibold">Rubric Template Library</h2>
          <button
            onClick={() => setShowTemplateLibrary(false)}
            className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
          >
            Back to Support Files
          </button>
        </div>
        <div className="flex-1 min-h-0">
          <TemplateLibrary />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Support Files</h2>
          <p className="text-sm text-muted-foreground">
            Load rubric, marking guide, and guidelines for grading
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowTemplateLibrary(true)}
            className="flex items-center gap-2 rounded-md border border-primary px-4 py-2 text-primary hover:bg-primary/10"
          >
            <BookOpen className="h-4 w-4" />
            Template Library
          </button>
          <button
            onClick={handleBrowseFiles}
            disabled={isLoading}
            className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            <Upload className="h-4 w-4" />
            Browse Files
          </button>
          {Object.keys(supportFiles).length > 0 && (
            <button
              onClick={handleClearAll}
              className="rounded-md border border-destructive px-4 py-2 text-destructive hover:bg-destructive/10"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Status Overview */}
      <div className={cn(
        "rounded-lg border p-4",
        allRequiredLoaded ? "border-green-200 bg-green-50" : "border-orange-200 bg-orange-50"
      )}>
        <div className="flex items-center gap-2">
          {allRequiredLoaded ? (
            <CheckCircle className="h-5 w-5 text-green-600" />
          ) : (
            <AlertCircle className="h-5 w-5 text-orange-600" />
          )}
          <span className={cn(
            "font-medium",
            allRequiredLoaded ? "text-green-800" : "text-orange-800"
          )}>
            {allRequiredLoaded 
              ? "All required support files loaded - Ready to grade" 
              : "Missing required support files"
            }
          </span>
        </div>
      </div>

      {/* Support File List */}
      <div className="grid gap-4">
        {supportFileTypes.map((fileType) => {
          const file = supportFiles[fileType.key]
          const isLoaded = file?.loaded

          return (
            <div
              key={fileType.key}
              className={cn(
                "rounded-lg border p-4 transition-colors",
                isLoaded ? "border-green-200 bg-green-50/50" : "border-gray-200"
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className={cn(
                    "h-3 w-3 rounded-full mt-2",
                    isLoaded ? "bg-green-500" : fileType.required ? "bg-red-500" : "bg-gray-400"
                  )} />
                  <div>
                    <h3 className="font-medium">
                      {fileType.label}
                      {fileType.required && <span className="text-red-500 ml-1">*</span>}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-2">
                      {fileType.description}
                    </p>
                    {isLoaded && file && (
                      <div className="text-xs text-muted-foreground">
                        <div className="flex items-center gap-2">
                          <FileText className="h-3 w-3" />
                          <span>{file.name}</span>
                          <span>({file.content.length} characters)</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                {isLoaded && (
                  <button
                    onClick={() => handleRemoveFile(fileType.key)}
                    className="rounded p-1 hover:bg-destructive/20"
                    title="Remove file"
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Assignment Specification Preview */}
      {supportFiles.assignmentSpec?.loaded && (
        <div className="rounded-lg border bg-blue-50/50 p-4">
          <h4 className="font-medium mb-3 text-blue-800">Assignment Specification Analysis</h4>
          <AssignmentSpecPreview />
        </div>
      )}

      {/* Instructions */}
      <div className="rounded-lg border bg-muted/50 p-4">
        <h4 className="font-medium mb-2">Loading Instructions</h4>
        <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
          <li>Select all three required files when browsing</li>
          <li>Files are automatically assigned based on filename keywords</li>
          <li>Supported formats: .docx, .doc, .pdf, .txt</li>
          <li>All three files must be loaded before grading can begin</li>
          <li>Assignment specification is optional but provides enhanced context</li>
        </ul>
      </div>
    </div>
  )
}