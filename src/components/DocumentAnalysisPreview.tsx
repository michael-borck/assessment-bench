import { useState, useEffect } from 'react'
import { BarChart3, FileText, Target, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { documentAnalysisAPI, type DocumentAnalysisResponse } from '../lib/documentAnalysis'
import { useAppStore } from '../stores/useAppStore'
import { cn } from '../lib/utils'

interface DocumentAnalysisPreviewProps {
  content: string
}

export function DocumentAnalysisPreview({ content }: DocumentAnalysisPreviewProps) {
  const { documentAnalysisConfig } = useAppStore()
  const [analysis, setAnalysis] = useState<DocumentAnalysisResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (content && documentAnalysisConfig.enabled) {
      performAnalysis()
    }
  }, [content, documentAnalysisConfig])

  const performAnalysis = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Configure API with current settings
      documentAnalysisAPI.setConfiguration(
        documentAnalysisConfig.baseUrl, 
        documentAnalysisConfig.apiKey
      )

      const response = await documentAnalysisAPI.analyzeDocument({
        content,
        expectedCitationStyle: 'APA' // Could be made configurable
      })

      setAnalysis(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setIsLoading(false)
    }
  }

  if (!documentAnalysisConfig.enabled) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <div className="flex items-center gap-2 text-gray-600">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">Document analysis is disabled</span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border bg-blue-50 p-4">
        <div className="flex items-center gap-2 text-blue-700">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span className="text-sm">Analyzing document...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="flex items-center gap-2 text-red-700">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">Analysis failed: {error}</span>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return null
  }

  const metrics = analysis.metrics

  const getScoreColor = (score: number, reverse: boolean = false) => {
    if (reverse) {
      if (score >= 80) return 'text-red-600'
      if (score >= 60) return 'text-yellow-600'
      return 'text-green-600'
    } else {
      if (score >= 80) return 'text-green-600'
      if (score >= 60) return 'text-yellow-600'
      return 'text-red-600'
    }
  }

  const getScoreBg = (score: number, reverse: boolean = false) => {
    if (reverse) {
      if (score >= 80) return 'bg-red-50 border-red-200'
      if (score >= 60) return 'bg-yellow-50 border-yellow-200'
      return 'bg-green-50 border-green-200'
    } else {
      if (score >= 80) return 'bg-green-50 border-green-200'
      if (score >= 60) return 'bg-yellow-50 border-yellow-200'
      return 'bg-red-50 border-red-200'
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <BarChart3 className="h-5 w-5 text-blue-600" />
        <h4 className="font-medium text-blue-800">Document Analysis Results</h4>
        {analysis.success ? (
          <CheckCircle className="h-4 w-4 text-green-500" />
        ) : (
          <AlertCircle className="h-4 w-4 text-red-500" />
        )}
      </div>

      {/* Quick Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="text-center p-3 rounded-lg bg-blue-50 border border-blue-200">
          <div className="text-lg font-semibold text-blue-700">{metrics.wordCount}</div>
          <div className="text-xs text-blue-600">Words</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-purple-50 border border-purple-200">
          <div className="text-lg font-semibold text-purple-700">{metrics.fleschKincaidGradeLevel.toFixed(1)}</div>
          <div className="text-xs text-purple-600">Grade Level</div>
        </div>
        <div className="text-center p-3 rounded-lg bg-indigo-50 border border-indigo-200">
          <div className="text-lg font-semibold text-indigo-700">{metrics.citationCount}</div>
          <div className="text-xs text-indigo-600">Citations</div>
        </div>
        <div className={cn(
          "text-center p-3 rounded-lg border",
          getScoreBg(metrics.grammarScore)
        )}>
          <div className={cn("text-lg font-semibold", getScoreColor(metrics.grammarScore))}>
            {metrics.grammarScore.toFixed(0)}%
          </div>
          <div className="text-xs text-muted-foreground">Grammar</div>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Readability Section */}
        <div className="space-y-3">
          <h5 className="font-medium text-gray-700 flex items-center gap-2">
            <Target className="h-4 w-4" />
            Readability & Complexity
          </h5>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Flesch Reading Ease:</span>
              <span className={getScoreColor(metrics.fleschReadingEase)}>
                {metrics.fleschReadingEase.toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Gunning Fog Index:</span>
              <span>{metrics.gunningFogIndex.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span>Complex Words:</span>
              <span className={getScoreColor(metrics.complexWordsPercentage, true)}>
                {metrics.complexWordsPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Academic Vocabulary:</span>
              <span className={getScoreColor(metrics.academicVocabularyPercentage)}>
                {metrics.academicVocabularyPercentage.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Structure Section */}
        <div className="space-y-3">
          <h5 className="font-medium text-gray-700 flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Structure & Citations
          </h5>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span>Paragraphs:</span>
              <span>{metrics.paragraphCount}</span>
            </div>
            <div className="flex justify-between">
              <span>Avg Words/Sentence:</span>
              <span>{metrics.averageWordsPerSentence.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span>Citation Compliance:</span>
              <span className={getScoreColor(metrics.citationFormatCompliance)}>
                {metrics.citationFormatCompliance.toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Structural Coherence:</span>
              <span className={getScoreColor(metrics.structuralCoherence)}>
                {metrics.structuralCoherence.toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Structural Elements */}
      <div className="rounded-lg bg-gray-50 p-3">
        <h5 className="font-medium text-gray-700 mb-2">Document Structure</h5>
        <div className="flex flex-wrap gap-2 text-xs">
          <span className={cn(
            "px-2 py-1 rounded",
            metrics.hasIntroduction 
              ? "bg-green-100 text-green-700" 
              : "bg-red-100 text-red-700"
          )}>
            Introduction: {metrics.hasIntroduction ? '✓' : '✗'}
          </span>
          <span className={cn(
            "px-2 py-1 rounded",
            metrics.hasConclusion 
              ? "bg-green-100 text-green-700" 
              : "bg-red-100 text-red-700"
          )}>
            Conclusion: {metrics.hasConclusion ? '✓' : '✗'}
          </span>
          <span className="px-2 py-1 rounded bg-blue-100 text-blue-700">
            Headings: {metrics.headingCount}
          </span>
          {metrics.spellingErrors > 0 && (
            <span className="px-2 py-1 rounded bg-red-100 text-red-700">
              Spelling errors: {metrics.spellingErrors}
            </span>
          )}
        </div>
      </div>

      {/* Suggestions and Warnings */}
      {((analysis.suggestions && analysis.suggestions.length > 0) || (analysis.warnings && analysis.warnings.length > 0)) && (
        <div className="space-y-2">
          {analysis.suggestions && analysis.suggestions.length > 0 && (
            <div className="rounded-lg bg-blue-50 border border-blue-200 p-3">
              <h6 className="font-medium text-blue-800 mb-1">Suggestions:</h6>
              <ul className="text-xs text-blue-700 space-y-1">
                {analysis.suggestions.map((suggestion, index) => (
                  <li key={index}>• {suggestion}</li>
                ))}
              </ul>
            </div>
          )}
          
          {analysis.warnings && analysis.warnings.length > 0 && (
            <div className="rounded-lg bg-yellow-50 border border-yellow-200 p-3">
              <h6 className="font-medium text-yellow-800 mb-1">Warnings:</h6>
              <ul className="text-xs text-yellow-700 space-y-1">
                {analysis.warnings.map((warning, index) => (
                  <li key={index}>• {warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}