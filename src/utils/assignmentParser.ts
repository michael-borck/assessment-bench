// Assignment Specification Parser
// Extracts rubrics, learning objectives, and requirements from assignment documents

export interface ParsedAssignmentSpec {
  title?: string
  learningObjectives: string[]
  requirements: string[]
  embeddedRubric?: EmbeddedRubric
  contextInfo: string[]
  deliverables: string[]
  deadline?: string
  wordCount?: {
    min?: number
    max?: number
  }
}

export interface EmbeddedRubric {
  criteria: EmbeddedCriterion[]
  totalPoints: number
  gradingScale?: string
}

export interface EmbeddedCriterion {
  name: string
  description: string
  points: number
  levels?: string[]
}

/**
 * Parse assignment specification text to extract structured information
 */
export function parseAssignmentSpecification(content: string): ParsedAssignmentSpec {
  const result: ParsedAssignmentSpec = {
    learningObjectives: [],
    requirements: [],
    contextInfo: [],
    deliverables: []
  }

  // Extract title (usually first significant line or header)
  const titleMatch = content.match(/^#?\s*(.+?)(?:\n|$)/m)
  if (titleMatch) {
    result.title = titleMatch[1].trim()
  }

  // Extract learning objectives
  result.learningObjectives = extractSection(content, [
    'learning objectives?',
    'course objectives?',
    'goals?',
    'aims?'
  ])

  // Extract requirements
  result.requirements = extractSection(content, [
    'requirements?',
    'specifications?',
    'criteria',
    'what you need to',
    'you must',
    'students? should'
  ])

  // Extract deliverables
  result.deliverables = extractSection(content, [
    'deliverables?',
    'submissions?',
    'what to submit',
    'submit the following'
  ])

  // Extract context information
  result.contextInfo = extractSection(content, [
    'background',
    'context',
    'introduction',
    'overview'
  ])

  // Try to extract embedded rubric
  result.embeddedRubric = extractEmbeddedRubric(content)

  // Extract deadline
  const deadlineMatch = content.match(/(?:due|deadline|submit by)[\s:]*([^\n]+)/i)
  if (deadlineMatch) {
    result.deadline = deadlineMatch[1].trim()
  }

  // Extract word count
  const wordCountMatch = content.match(/(\d+)[-–\s]*(\d+)?\s*words?/i)
  if (wordCountMatch) {
    result.wordCount = {
      min: parseInt(wordCountMatch[1]),
      max: wordCountMatch[2] ? parseInt(wordCountMatch[2]) : undefined
    }
  }

  return result
}

/**
 * Extract sections based on header patterns
 */
function extractSection(content: string, patterns: string[]): string[] {
  const items: string[] = []
  
  for (const pattern of patterns) {
    const regex = new RegExp(`(?:^|\\n)\\s*(?:#*\\s*)?${pattern}[:\\s]*\\n([^\\n#]+(?:\\n(?!\\n|#)[^\\n]*)*)`,'gi')
    const matches = content.matchAll(regex)
    
    for (const match of matches) {
      const sectionText = match[1]
      // Split by bullet points, numbered lists, or line breaks
      const sectionItems = sectionText
        .split(/(?:\n|^)\s*(?:[-•*]|\d+\.)\s*/)
        .filter(item => item.trim().length > 0)
        .map(item => item.trim().replace(/\n\s*/g, ' '))
      
      items.push(...sectionItems)
    }
  }

  return [...new Set(items)] // Remove duplicates
}

/**
 * Attempt to extract an embedded rubric from the assignment specification
 */
function extractEmbeddedRubric(content: string): EmbeddedRubric | undefined {
  const criteria: EmbeddedCriterion[] = []
  let totalPoints = 0

  // Look for rubric sections
  const rubricMatch = content.match(/(?:rubric|grading\s*criteria|assessment\s*criteria)[:\s]*\n([\s\S]*?)(?:\n\n|\n#|$)/i)
  if (!rubricMatch) return undefined

  const rubricSection = rubricMatch[1]

  // Extract criteria with points
  const criteriaMatches = rubricSection.matchAll(/(?:^|\n)\s*(?:[-•*]|\d+\.)\s*([^(\n]+)\s*\((\d+)\s*points?\)/gi)
  
  for (const match of criteriaMatches) {
    const name = match[1].trim()
    const points = parseInt(match[2])
    
    criteria.push({
      name,
      description: name, // Use name as description for now
      points
    })
    
    totalPoints += points
  }

  // Alternative pattern: table-like format
  if (criteria.length === 0) {
    const tableMatches = content.matchAll(/([^|\n]+)\s*\|\s*(\d+)/g)
    for (const match of tableMatches) {
      const name = match[1].trim()
      const points = parseInt(match[2])
      
      if (name && points > 0) {
        criteria.push({
          name,
          description: name,
          points
        })
        totalPoints += points
      }
    }
  }

  if (criteria.length === 0) return undefined

  return {
    criteria,
    totalPoints,
    gradingScale: extractGradingScale(content)
  }
}

/**
 * Extract grading scale information
 */
function extractGradingScale(content: string): string | undefined {
  const scalePatterns = [
    /grading\s*scale[:\s]*([^\n]+)/i,
    /(?:a|a\+)[:\s=]*\s*(\d+)[-–](\d+)%/i,
    /excellent[:\s=]*\s*(\d+)[-–](\d+)/i
  ]

  for (const pattern of scalePatterns) {
    const match = content.match(pattern)
    if (match) {
      return match[0].trim()
    }
  }

  return undefined
}

/**
 * Generate enhanced prompts using assignment specification context
 */
export function enhancePromptWithAssignmentSpec(
  basePrompt: string,
  assignmentSpec: ParsedAssignmentSpec
): string {
  let enhancedPrompt = basePrompt

  // Add assignment context
  if (assignmentSpec.title) {
    enhancedPrompt += `\n\n**Assignment Title**: ${assignmentSpec.title}`
  }

  // Add learning objectives
  if (assignmentSpec.learningObjectives.length > 0) {
    enhancedPrompt += `\n\n**Learning Objectives**:\n${assignmentSpec.learningObjectives.map(obj => `- ${obj}`).join('\n')}`
  }

  // Add requirements
  if (assignmentSpec.requirements.length > 0) {
    enhancedPrompt += `\n\n**Assignment Requirements**:\n${assignmentSpec.requirements.map(req => `- ${req}`).join('\n')}`
  }

  // Add deliverables
  if (assignmentSpec.deliverables.length > 0) {
    enhancedPrompt += `\n\n**Expected Deliverables**:\n${assignmentSpec.deliverables.map(del => `- ${del}`).join('\n')}`
  }

  // Add embedded rubric information
  if (assignmentSpec.embeddedRubric) {
    enhancedPrompt += `\n\n**Embedded Rubric Criteria**:\n${assignmentSpec.embeddedRubric.criteria.map(crit => `- ${crit.name}: ${crit.points} points`).join('\n')}`
    enhancedPrompt += `\nTotal Points: ${assignmentSpec.embeddedRubric.totalPoints}`
  }

  // Add word count constraints
  if (assignmentSpec.wordCount) {
    const { min, max } = assignmentSpec.wordCount
    if (min && max) {
      enhancedPrompt += `\n\n**Word Count Requirement**: ${min}-${max} words`
    } else if (min) {
      enhancedPrompt += `\n\n**Minimum Word Count**: ${min} words`
    }
  }

  enhancedPrompt += `\n\n**Grading Instruction**: Use the above assignment context to inform your evaluation. Ensure submissions meet the stated requirements and align with learning objectives.`

  return enhancedPrompt
}