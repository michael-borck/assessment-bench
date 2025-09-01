import { Check, Zap, Brain, FileText, BarChart3 } from 'lucide-react'
import { useAppStore, type WorkflowType } from '../stores/useAppStore'
import { cn } from '../lib/utils'

export function WorkflowSelector() {
  const { currentWorkflow, setCurrentWorkflow } = useAppStore()

  const workflows = [
    {
      type: 'basic' as WorkflowType,
      name: 'Basic Grading',
      icon: Zap,
      description: 'Direct LLM grading with rubric and support files',
      features: [
        'Student essay + rubric',
        'Custom grading prompts',
        'Multiple LLM providers',
        'Fast processing'
      ],
      ideal: 'Quick grading sessions and simple assessments'
    },
    {
      type: 'enhanced' as WorkflowType,
      name: 'Enhanced Analysis',
      icon: Brain,
      description: 'Document analysis + LLM grading for comprehensive assessment',
      features: [
        'Automatic document analysis',
        'Readability & complexity scores',
        'Citation & reference checking',
        'Enhanced grading context',
        'Research-grade metrics'
      ],
      ideal: 'Research studies and detailed academic assessments'
    }
  ]

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold mb-2">Select Grading Workflow</h3>
        <p className="text-sm text-muted-foreground">
          Choose how you want to process and grade student submissions
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {workflows.map((workflow) => {
          const Icon = workflow.icon
          const isSelected = currentWorkflow === workflow.type
          
          return (
            <div
              key={workflow.type}
              className={cn(
                "relative rounded-lg border p-6 cursor-pointer transition-all hover:shadow-md",
                isSelected
                  ? "border-primary bg-primary/5 ring-2 ring-primary/20"
                  : "border-gray-200 hover:border-primary/50"
              )}
              onClick={() => setCurrentWorkflow(workflow.type)}
            >
              {isSelected && (
                <div className="absolute top-4 right-4 h-6 w-6 rounded-full bg-primary flex items-center justify-center">
                  <Check className="h-4 w-4 text-primary-foreground" />
                </div>
              )}
              
              <div className="flex items-start gap-4">
                <div className={cn(
                  "flex h-12 w-12 items-center justify-center rounded-lg",
                  isSelected ? "bg-primary/10" : "bg-muted"
                )}>
                  <Icon className={cn(
                    "h-6 w-6",
                    isSelected ? "text-primary" : "text-muted-foreground"
                  )} />
                </div>
                
                <div className="flex-1">
                  <h4 className="font-medium mb-1">{workflow.name}</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    {workflow.description}
                  </p>
                  
                  <div className="space-y-2">
                    <h5 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      Features
                    </h5>
                    <ul className="space-y-1">
                      {workflow.features.map((feature, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm">
                          <div className="w-1.5 h-1.5 rounded-full bg-primary/60 flex-shrink-0" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t">
                    <div className="flex items-start gap-2">
                      <FileText className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-1">
                          Ideal for:
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {workflow.ideal}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Enhanced Workflow Additional Info */}
      {currentWorkflow === 'enhanced' && (
        <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-4">
          <div className="flex items-start gap-3">
            <BarChart3 className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Enhanced Analysis Features</h4>
              <div className="grid sm:grid-cols-2 gap-2 text-sm text-blue-700">
                <div>• Word count & structure analysis</div>
                <div>• Readability scores (Flesch-Kincaid)</div>
                <div>• Citation format validation</div>
                <div>• Academic vocabulary assessment</div>
                <div>• Paragraph coherence metrics</div>
                <div>• Reference completeness check</div>
              </div>
              <p className="text-xs text-blue-600 mt-2">
                These metrics will be provided to the LLM alongside your rubric for more informed grading decisions.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}