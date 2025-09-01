import type { RubricTemplate } from '../types/templates'

// Helper function to create performance levels
const createStandardLevels = (maxPoints: number) => [
  {
    level: "Excellent",
    description: "Exceeds expectations with exceptional quality and insight",
    points: maxPoints
  },
  {
    level: "Good", 
    description: "Meets expectations with solid understanding and execution",
    points: Math.round(maxPoints * 0.8)
  },
  {
    level: "Satisfactory",
    description: "Adequate work that meets basic requirements",
    points: Math.round(maxPoints * 0.6)
  },
  {
    level: "Needs Improvement",
    description: "Below expectations, requires significant revision",
    points: Math.round(maxPoints * 0.4)
  },
  {
    level: "Unsatisfactory",
    description: "Does not meet basic requirements",
    points: 0
  }
]

// Essay Templates
const argumentativeEssayTemplate: RubricTemplate = {
  id: 'argumentative-essay-standard',
  name: 'Argumentative Essay - Standard',
  category: 'essays',
  description: 'Standard rubric for argumentative essays with thesis, evidence, and counterarguments',
  totalPoints: 100,
  createdBy: 'system',
  createdAt: '2024-01-01T00:00:00Z',
  tags: ['argument', 'persuasive', 'thesis', 'evidence'],
  criteria: [
    {
      id: 'thesis-clarity',
      name: 'Thesis & Argument Clarity',
      description: 'Clear, focused thesis statement with well-developed argument',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'evidence-support',
      name: 'Evidence & Supporting Details',
      description: 'Relevant, credible evidence that effectively supports the argument',
      maxPoints: 25,
      performanceLevels: createStandardLevels(25)
    },
    {
      id: 'counterarguments',
      name: 'Counterarguments & Refutation',
      description: 'Acknowledges and addresses opposing viewpoints effectively',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'organization',
      name: 'Organization & Structure',
      description: 'Logical flow with clear introduction, body, and conclusion',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'writing-quality',
      name: 'Writing Quality & Style',
      description: 'Clear, engaging prose with varied sentence structure',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'grammar-mechanics',
      name: 'Grammar & Mechanics',
      description: 'Proper grammar, punctuation, and spelling',
      maxPoints: 10,
      performanceLevels: createStandardLevels(10)
    }
  ]
}

const analyticalEssayTemplate: RubricTemplate = {
  id: 'analytical-essay-standard',
  name: 'Analytical Essay - Literary Analysis',
  category: 'essays',
  description: 'Rubric for literary or text analysis essays',
  totalPoints: 100,
  createdBy: 'system',
  createdAt: '2024-01-01T00:00:00Z',
  tags: ['analysis', 'literary', 'interpretation', 'textual-evidence'],
  criteria: [
    {
      id: 'thesis-interpretation',
      name: 'Thesis & Interpretation',
      description: 'Clear, insightful thesis that presents original interpretation',
      maxPoints: 25,
      performanceLevels: createStandardLevels(25)
    },
    {
      id: 'textual-evidence',
      name: 'Textual Evidence & Citations',
      description: 'Effective use of relevant quotations and examples from the text',
      maxPoints: 25,
      performanceLevels: createStandardLevels(25)
    },
    {
      id: 'analysis-depth',
      name: 'Depth of Analysis',
      description: 'Thoughtful analysis that goes beyond surface-level observations',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'organization',
      name: 'Organization & Development',
      description: 'Well-structured argument with logical progression of ideas',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'writing-style',
      name: 'Writing Style & Voice',
      description: 'Appropriate academic tone with clear, precise language',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    }
  ]
}

// Technical Writing Templates
const labReportTemplate: RubricTemplate = {
  id: 'lab-report-standard',
  name: 'Laboratory Report - Science',
  category: 'technical-writing',
  description: 'Standard rubric for scientific laboratory reports',
  totalPoints: 100,
  createdBy: 'system',
  createdAt: '2024-01-01T00:00:00Z',
  tags: ['lab-report', 'scientific-method', 'data-analysis'],
  criteria: [
    {
      id: 'abstract-summary',
      name: 'Abstract & Summary',
      description: 'Concise summary of purpose, methods, results, and conclusions',
      maxPoints: 10,
      performanceLevels: createStandardLevels(10)
    },
    {
      id: 'introduction-hypothesis',
      name: 'Introduction & Hypothesis',
      description: 'Clear background, purpose, and testable hypothesis',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'methodology',
      name: 'Methods & Procedures',
      description: 'Detailed, reproducible experimental procedures',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'results-data',
      name: 'Results & Data Presentation',
      description: 'Clear presentation of data with appropriate tables/graphs',
      maxPoints: 25,
      performanceLevels: createStandardLevels(25)
    },
    {
      id: 'discussion-analysis',
      name: 'Discussion & Analysis',
      description: 'Thoughtful interpretation of results and their significance',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'technical-writing',
      name: 'Technical Writing Quality',
      description: 'Clear, precise scientific writing with proper terminology',
      maxPoints: 10,
      performanceLevels: createStandardLevels(10)
    }
  ]
}

// Research Paper Template
const researchPaperTemplate: RubricTemplate = {
  id: 'research-paper-standard',
  name: 'Research Paper - Academic',
  category: 'academic-papers',
  description: 'Comprehensive rubric for academic research papers',
  totalPoints: 100,
  createdBy: 'system',
  createdAt: '2024-01-01T00:00:00Z',
  tags: ['research', 'academic', 'citations', 'methodology'],
  criteria: [
    {
      id: 'research-question',
      name: 'Research Question & Thesis',
      description: 'Clear, focused research question with well-defined thesis',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'literature-review',
      name: 'Literature Review & Background',
      description: 'Comprehensive review of relevant scholarly sources',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'methodology-approach',
      name: 'Methodology & Approach',
      description: 'Appropriate research methods and analytical framework',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'analysis-findings',
      name: 'Analysis & Findings',
      description: 'Thorough analysis with clear presentation of findings',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'citations-references',
      name: 'Citations & References',
      description: 'Proper citation format and credible sources',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'academic-writing',
      name: 'Academic Writing Quality',
      description: 'Scholarly tone, clear arguments, and professional presentation',
      maxPoints: 10,
      performanceLevels: createStandardLevels(10)
    }
  ]
}

// Code Assignment Template
const codingAssignmentTemplate: RubricTemplate = {
  id: 'coding-assignment-standard',
  name: 'Programming Assignment - General',
  category: 'code-assignments',
  description: 'Standard rubric for programming assignments and projects',
  totalPoints: 100,
  createdBy: 'system',
  createdAt: '2024-01-01T00:00:00Z',
  tags: ['programming', 'code-quality', 'algorithms', 'testing'],
  criteria: [
    {
      id: 'correctness-functionality',
      name: 'Correctness & Functionality',
      description: 'Program works correctly and meets all requirements',
      maxPoints: 35,
      performanceLevels: createStandardLevels(35)
    },
    {
      id: 'code-quality',
      name: 'Code Quality & Style',
      description: 'Clean, readable code following best practices',
      maxPoints: 20,
      performanceLevels: createStandardLevels(20)
    },
    {
      id: 'algorithm-efficiency',
      name: 'Algorithm & Efficiency',
      description: 'Appropriate algorithms with good time/space complexity',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'documentation',
      name: 'Documentation & Comments',
      description: 'Clear comments and documentation explaining the code',
      maxPoints: 15,
      performanceLevels: createStandardLevels(15)
    },
    {
      id: 'error-handling',
      name: 'Error Handling & Edge Cases',
      description: 'Proper handling of errors and edge cases',
      maxPoints: 10,
      performanceLevels: createStandardLevels(10)
    },
    {
      id: 'testing',
      name: 'Testing & Validation',
      description: 'Adequate testing with test cases and validation',
      maxPoints: 5,
      performanceLevels: createStandardLevels(5)
    }
  ]
}

// Export all built-in templates
export const BUILT_IN_TEMPLATES: RubricTemplate[] = [
  argumentativeEssayTemplate,
  analyticalEssayTemplate,
  labReportTemplate,
  researchPaperTemplate,
  codingAssignmentTemplate
]

// Template categories metadata
export const TEMPLATE_CATEGORIES = {
  essays: {
    name: 'Essays',
    description: 'Rubrics for various types of essays and persuasive writing',
    icon: 'FileText'
  },
  'technical-writing': {
    name: 'Technical Writing', 
    description: 'Lab reports, technical documentation, and scientific writing',
    icon: 'Beaker'
  },
  'creative-writing': {
    name: 'Creative Writing',
    description: 'Poetry, short stories, and creative expression assignments',
    icon: 'Feather'
  },
  'academic-papers': {
    name: 'Academic Papers',
    description: 'Research papers, literature reviews, and scholarly writing',
    icon: 'GraduationCap'
  },
  'code-assignments': {
    name: 'Code Assignments',
    description: 'Programming projects and computer science assignments', 
    icon: 'Code'
  },
  custom: {
    name: 'Custom Templates',
    description: 'User-created templates and imported rubrics',
    icon: 'Settings'
  }
} as const