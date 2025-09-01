import React from 'react'
import { FileText, Target, CheckSquare, Calendar, BookOpen, Award } from 'lucide-react'
import { useAppStore } from '../stores/useAppStore'
import { parseAssignmentSpecification, type ParsedAssignmentSpec } from '../utils/assignmentParser'
import { cn } from '../lib/utils'

export function AssignmentSpecPreview() {
  const { supportFiles } = useAppStore()
  const [parsedSpec, setParsedSpec] = React.useState<ParsedAssignmentSpec | null>(null)
  const [isLoading, setIsLoading] = React.useState(false)

  const assignmentSpec = supportFiles.assignmentSpec

  React.useEffect(() => {
    if (assignmentSpec?.content) {
      setIsLoading(true)
      try {
        const parsed = parseAssignmentSpecification(assignmentSpec.content)
        setParsedSpec(parsed)
      } catch (error) {
        console.error('Error parsing assignment specification:', error)
      } finally {
        setIsLoading(false)
      }
    } else {
      setParsedSpec(null)
    }
  }, [assignmentSpec?.content])

  if (!assignmentSpec?.loaded) {
    return (
      <div className="text-center py-8">
        <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">No assignment specification loaded</p>
        <p className="text-xs text-muted-foreground mt-1">
          Load an assignment document to see parsed context and requirements
        </p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-muted-foreground">Analyzing assignment specification...</p>
      </div>
    )
  }

  if (!parsedSpec) {
    return (
      <div className="text-center py-8">
        <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
        <p className="text-muted-foreground">Could not parse assignment specification</p>
        <p className="text-xs text-muted-foreground mt-1">
          The document may not contain standard assignment structure
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
          <FileText className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold">
            {parsedSpec.title || assignmentSpec.name}
          </h3>
          <p className="text-sm text-muted-foreground">
            Assignment specification analysis
          </p>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-3 rounded-lg bg-muted/50">
          <div className="text-lg font-semibold text-primary">
            {parsedSpec.learningObjectives.length}
          </div>
          <div className="text-xs text-muted-foreground">Learning Objectives</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-muted/50">
          <div className="text-lg font-semibold text-primary">
            {parsedSpec.requirements.length}
          </div>
          <div className="text-xs text-muted-foreground">Requirements</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-muted/50">
          <div className="text-lg font-semibold text-primary">
            {parsedSpec.deliverables.length}
          </div>
          <div className="text-xs text-muted-foreground">Deliverables</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-muted/50">
          <div className={cn(
            "text-lg font-semibold",
            parsedSpec.embeddedRubric ? "text-green-600" : "text-muted-foreground"
          )}>
            {parsedSpec.embeddedRubric ? '✓' : '✗'}
          </div>
          <div className="text-xs text-muted-foreground">Embedded Rubric</div>
        </div>
      </div>

      {/* Learning Objectives */}
      {parsedSpec.learningObjectives.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            <h4 className="font-medium">Learning Objectives</h4>
          </div>
          <div className="space-y-1">
            {parsedSpec.learningObjectives.map((objective, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2 flex-shrink-0" />
                <span>{objective}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Requirements */}
      {parsedSpec.requirements.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <CheckSquare className="h-4 w-4 text-primary" />
            <h4 className="font-medium">Requirements</h4>
          </div>
          <div className="space-y-1">
            {parsedSpec.requirements.map((requirement, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2 flex-shrink-0" />
                <span>{requirement}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Deliverables */}
      {parsedSpec.deliverables.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-primary" />
            <h4 className="font-medium">Deliverables</h4>
          </div>
          <div className="space-y-1">
            {parsedSpec.deliverables.map((deliverable, index) => (
              <div key={index} className="flex items-start gap-2 text-sm">
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 mt-2 flex-shrink-0" />
                <span>{deliverable}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Embedded Rubric */}
      {parsedSpec.embeddedRubric && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Award className="h-4 w-4 text-green-600" />
            <h4 className="font-medium text-green-800">Embedded Rubric Detected</h4>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div>
                <span className="text-sm font-medium">Total Points: </span>
                <span className="text-sm">{parsedSpec.embeddedRubric.totalPoints}</span>
              </div>
              <div>
                <span className="text-sm font-medium">Criteria: </span>
                <span className="text-sm">{parsedSpec.embeddedRubric.criteria.length}</span>
              </div>
            </div>
            <div className="space-y-1">
              {parsedSpec.embeddedRubric.criteria.map((criterion, index) => (
                <div key={index} className="flex justify-between items-center text-sm">
                  <span>{criterion.name}</span>
                  <span className="font-mono text-green-700">{criterion.points}pts</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Additional Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {parsedSpec.wordCount && (
          <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
            <div className="flex items-center gap-2 mb-1">
              <Calendar className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Word Count</span>
            </div>
            <div className="text-sm text-blue-700">
              {parsedSpec.wordCount.min && parsedSpec.wordCount.max
                ? `${parsedSpec.wordCount.min}-${parsedSpec.wordCount.max} words`
                : parsedSpec.wordCount.min
                ? `Minimum ${parsedSpec.wordCount.min} words`
                : 'Word count specified'}
            </div>
          </div>
        )}

        {parsedSpec.deadline && (
          <div className="p-3 rounded-lg bg-orange-50 border border-orange-200">
            <div className="flex items-center gap-2 mb-1">
              <Calendar className="h-4 w-4 text-orange-600" />
              <span className="text-sm font-medium text-orange-800">Deadline</span>
            </div>
            <div className="text-sm text-orange-700">{parsedSpec.deadline}</div>
          </div>
        )}
      </div>

      {/* Context Information */}
      {parsedSpec.contextInfo.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-muted-foreground">Context Information</h4>
          <div className="text-sm text-muted-foreground space-y-1">
            {parsedSpec.contextInfo.slice(0, 3).map((info, index) => (
              <div key={index} className="flex items-start gap-2">
                <div className="w-1 h-1 rounded-full bg-muted-foreground/60 mt-2 flex-shrink-0" />
                <span>{info}</span>
              </div>
            ))}
            {parsedSpec.contextInfo.length > 3 && (
              <div className="text-xs text-muted-foreground/60">
                +{parsedSpec.contextInfo.length - 3} more items...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}