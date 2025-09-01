# AI Assessor - Comprehensive Specification

## Executive Summary

AI Assessor is a desktop application designed for educators and researchers to evaluate AI-powered grading systems. The application implements a Three-Tier Grading System with comprehensive analysis capabilities, post-processing validation, and comparative assessment tools. Built as a Tauri application for complete data control and privacy.

## Table of Contents
1. [Application Overview](#application-overview)
2. [Core Philosophy](#core-philosophy)
3. [Three-Tier Grading System](#three-tier-grading-system)
4. [Improved Workflow Design](#improved-workflow-design)
5. [Architecture](#architecture)
6. [User Interface Specification](#user-interface-specification)
7. [File Management](#file-management)
8. [Integration Specifications](#integration-specifications)
9. [Comparison and Analytics](#comparison-and-analytics)
10. [Technical Implementation](#technical-implementation)

## Application Overview

### Purpose
AI Assessor enables systematic comparison of AI grading approaches to determine optimal configurations for different assignment types and contexts. The application serves both practical grading needs and research objectives.

### Key Capabilities
- **Multi-Tier Grading**: Three distinct approaches from basic to comprehensive
- **Provider Agnostic**: Support for OpenAI, Anthropic, Google, Ollama, and custom endpoints  
- **Research Tools**: Comparative analysis, consistency testing, and statistical visualization
- **Complete Privacy**: All data remains local, no server storage
- **Extensible Analysis**: Integration with DocumentLens microservice for advanced metrics

## Core Philosophy

### Data Sovereignty
- All submissions and results stored locally
- Original files copied to managed workspace
- No data transmitted to external servers except LLM APIs
- User maintains complete control over academic content

### Research-First Design
- Every operation generates metrics for analysis
- Comparative studies built into core workflow  
- Statistical tools integrated, not bolted-on
- Reproducible experiments with configuration versioning

### Educator-Friendly
- Intuitive interface requiring minimal technical knowledge
- Professional rubric management and templates
- Clear visualization of grading differences
- Export capabilities for institutional reporting

## Three-Tier Grading System

### Tier 1: Basic LLM
**Input**: Essay + Rubric → LLM
- Direct submission to LLM with rubric
- Minimal preprocessing
- Fastest processing time
- Baseline for comparison studies

### Tier 2: Enhanced LLM  
**Input**: Essay + Analysis + Rubric → LLM
- DocumentLens preprocessing for objective metrics
- Readability, writing quality, word analysis
- Enhanced context for subjective assessment
- Balance of automation and human-like judgment

### Tier 3: Assignment-Aware
**Input**: Essay + Analysis + Rubric + Assignment Specification → LLM
- Full context awareness
- Assignment-specific criteria integration
- Learning objective alignment
- Maximum contextual information

### Research Questions Enabled
- Does assignment specification improve accuracy?
- Which tier provides most consistent results?
- How does preprocessing affect different LLM models?
- What's the cost/benefit ratio of each tier?

## Improved Workflow Design

### Current Workflow Issues Identified
1. **Fragmented Setup**: Support files loaded separately without clear relationships
2. **Manual Configuration**: Repetitive setup for similar assessments  
3. **Limited Comparison**: Difficult to run same submission through multiple approaches
4. **Results Isolation**: No integrated view of different grading attempts

### Proposed Improved Workflow

#### 1. Project-Centric Organization
```
Assessment Project Structure:
├── project-config.json
├── submissions/
│   ├── original/        # Read-only copies
│   └── processed/       # Extracted text, analysis cache
├── support-files/
│   ├── rubric.json
│   ├── marking-guide.md
│   └── assignment-spec.pdf
├── results/
│   ├── basic/
│   ├── enhanced/
│   └── assignment-aware/
└── reports/
    ├── comparison-reports/
    └── statistical-analysis/
```

#### 2. Streamlined Setup Flow
**Step 1: Project Creation**
- Name and describe assessment project
- Select or create rubric template
- Define grading tiers to evaluate

**Step 2: Context Loading**
- Upload/select assignment specification
- Import marking guidelines
- Configure LLM providers and models

**Step 3: Submission Management**  
- Drag-and-drop submission folder
- Automatic file detection and validation
- Preview submissions with basic metrics

**Step 4: Grading Execution**
- Select tiers to run (can run multiple)
- Configure repetition count for consistency testing
- Monitor progress with detailed logging

**Step 5: Analysis and Comparison**
- Side-by-side tier comparison
- Statistical analysis of score distributions
- Export results for further analysis

#### 3. Intelligent Defaults
- **Auto-detect assignment type** from specification content
- **Suggest appropriate tiers** based on assignment complexity
- **Pre-populate prompts** with contextually relevant instructions
- **Recommend repetition counts** based on model capabilities

#### 4. Unified Results Dashboard
- **Consistency Metrics**: Standard deviation, confidence intervals
- **Tier Comparison**: Score distribution plots, correlation analysis
- **Individual Review**: Drill-down to specific submissions and feedback
- **Export Options**: CSV, JSON, PDF reports for institutional use

## Architecture

### Desktop Application (Tauri)
- **Frontend**: React/TypeScript for rich user interface
- **Backend**: Rust for performance and system integration
- **Database**: SQLite for local data persistence
- **File System**: Structured project directories

### External Integrations
- **DocumentLens API**: Text and academic analysis microservice
- **LLM Providers**: OpenAI, Anthropic, Google, Ollama, custom endpoints
- **File Processors**: PDF, DOCX, TXT/Markdown extraction

### Data Flow
1. **Ingestion**: Files copied to managed workspace
2. **Preprocessing**: DocumentLens analysis (Tiers 2+3)
3. **Grading**: Parallel execution across selected tiers
4. **Post-processing**: Score extraction and validation
5. **Storage**: Results saved with full audit trail
6. **Analysis**: Statistical comparison and reporting

## User Interface Specification

### Main Application Layout
```
┌─ Menu Bar ─────────────────────────────────────────────────┐
├─ Toolbar (New Project, Open, Settings, Help) ─────────────├
├─ Project Navigator (Left Sidebar, 300px) ─────────────────├──┐
│  ├─ Current Project Info                                   │  │
│  ├─ Submissions (with status indicators)                   │  │
│  ├─ Support Files                                         │  │
│  └─ Recent Results                                        │  │
├─ Main Content Area ───────────────────────────────────────├──┤
│  ├─ Dynamic content based on selected section             │  │
│  └─ (Setup, Grading, Results, Comparison)                 │  │
├─ Status Bar ──────────────────────────────────────────────├──┘
└─ Progress Indicators (during grading operations) ─────────┘
```

### Key Interface Screens

#### 1. Project Setup Screen
- **Project Information Panel**: Name, description, creation date
- **Grading Configuration**: Select tiers, LLM providers, repetition count
- **Support Files Manager**: Upload/select rubric, guidelines, assignment spec
- **Submission Preview**: Thumbnails of loaded submissions with basic stats

#### 2. Grading Execution Screen
- **Real-time Progress**: Per-submission, per-tier progress bars
- **Live Log**: Streaming status updates and error messages
- **Resource Usage**: API calls, processing time, estimated completion
- **Quick Actions**: Pause, resume, cancel operations

#### 3. Results Dashboard
- **Overview Cards**: Total submissions, completion rate, average scores
- **Tier Comparison Chart**: Side-by-side score distributions
- **Consistency Analysis**: Box plots showing score variance
- **Individual Results Table**: Sortable, filterable submission results

#### 4. Detailed Analysis Screen
- **Submission Viewer**: Original text with highlighted analysis points
- **Side-by-side Feedback**: Compare LLM responses across tiers
- **Score Breakdown**: Rubric criteria with individual marks
- **Analysis Metrics**: DocumentLens results integrated with feedback

### Responsive Design Principles
- **Minimum Resolution**: 1280x768
- **Scalable Layout**: Adjustable panel sizes
- **Accessibility**: WCAG 2.1 AA compliance
- **Keyboard Navigation**: Full keyboard operation support

## File Management

### Project Structure
Each assessment project creates a self-contained directory with standardized structure for portability and organization.

### Submission Handling
1. **Import Process**: User selects files from any location
2. **Validation**: Check file formats, sizes, accessibility
3. **Copying**: Create read-only copies in project structure
4. **Processing**: Extract text and generate analysis cache
5. **Cleanup**: Automatic temporary file management

### Metadata Tracking
```json
{
  "project": {
    "id": "uuid",
    "name": "Essay Assessment Fall 2024",
    "created": "2024-01-15T10:00:00Z",
    "version": "1.0"
  },
  "submissions": [
    {
      "id": "uuid",
      "original_filename": "student_essay.pdf",
      "file_hash": "sha256_hash",
      "imported_at": "2024-01-15T10:05:00Z",
      "file_type": "pdf",
      "word_count": 1250,
      "status": "processed"
    }
  ],
  "grading_config": {
    "tiers_enabled": ["basic", "enhanced", "assignment-aware"],
    "providers": ["openai", "anthropic"],
    "repetitions": 3
  }
}
```

## Integration Specifications

### DocumentLens API Integration
The application integrates with the DocumentLens microservice for comprehensive text analysis.

#### Tier 2 Integration (Enhanced LLM)
- **Endpoint**: `POST /api/analyze/text`
- **Purpose**: Essential text metrics for general writing assessment
- **Data Used**:
  - Readability scores (Flesch, Flesch-Kincaid)  
  - Writing quality metrics (passive voice, sentence variety)
  - Word analysis (frequency, n-grams, vocabulary richness)
  - Basic text metrics (word/sentence/paragraph counts)

#### Tier 3 Integration (Assignment-Aware)  
- **Endpoint**: `POST /api/analyze/academic`
- **Purpose**: Specialized academic document analysis
- **Data Used**:
  - Citation extraction and style detection
  - DOI resolution and validation
  - URL verification with Wayback Machine
  - AI-generated content detection
  - Plagiarism indicators
  - Reference integrity checking

#### Document Upload Integration
- **Endpoint**: `POST /api/analyze`
- **Purpose**: Full document processing with multi-format support
- **Supported Formats**: PDF, DOCX, TXT, MD
- **Features**:
  - Automatic text extraction
  - Combined text + academic analysis
  - Document comparison capabilities

### LLM Provider Integration

#### OpenAI Integration
```typescript
interface OpenAIConfig {
  apiKey: string;
  model: string; // gpt-4-turbo, gpt-3.5-turbo, etc.
  temperature: number;
  maxTokens?: number;
  baseURL?: string; // For Azure OpenAI
}
```

#### Anthropic Integration  
```typescript
interface AnthropicConfig {
  apiKey: string;
  model: string; // claude-3-opus, claude-3-sonnet, etc.
  temperature: number;
  maxTokens?: number;
}
```

#### Ollama Integration
```typescript
interface OllamaConfig {
  baseURL: string; // http://localhost:11434
  model: string; // llama2, mistral, etc.
  temperature: number;
  jsonMode: boolean; // Enable for structured output
}
```

### JSON-Structured Output for Weak Models

For smaller/weaker models (particularly Ollama), the application uses structured JSON responses to improve reliability:

```json
{
  "overall_grade": "B+",
  "total_points": 85,
  "rubric_scores": [
    {
      "criterion": "Thesis and Argument",
      "points_awarded": 18,
      "points_possible": 20,
      "comments": "Clear thesis with strong supporting arguments"
    },
    {
      "criterion": "Evidence and Sources", 
      "points_awarded": 22,
      "points_possible": 25,
      "comments": "Good use of sources, could benefit from more diversity"
    }
  ],
  "summary_feedback": "Well-written essay with clear argumentation...",
  "strengths": ["Clear writing", "Strong thesis"],
  "improvements": ["More diverse sources", "Stronger conclusion"]
}
```

## Multiple Assessment Feature

### Consistency Testing
- **Repetition Control**: Configure 1-10 assessment runs per submission
- **Aggregation Methods**:
  - Mean score with confidence intervals
  - Median score (robust against outliers)
  - Mode identification for categorical grades
  - Standard deviation analysis

### Statistical Analysis
- **Score Distribution**: Histograms and box plots per tier/provider
- **Consistency Metrics**: 
  - Coefficient of variation
  - Inter-assessment reliability
  - Score stability analysis
- **Comparison Visualization**:
  - Single vs. multiple assessment plots
  - Convergence analysis (how scores stabilize with more runs)
  - Provider comparison matrices

## Comparison and Analytics

### Dashboard Overview
The analytics dashboard provides comprehensive comparison tools for different grading approaches.

#### Comparison Matrices
```
Provider/Tier Comparison Matrix:
                 Basic    Enhanced    Assignment-Aware
OpenAI GPT-4      85.2      87.1          88.5
Anthropic Claude  84.8      86.9          87.8  
Ollama Llama2     78.3      82.1          83.2
```

#### Statistical Visualizations
1. **Score Distribution Plots**: Histograms comparing tier effectiveness
2. **Consistency Charts**: Box plots showing score variance
3. **Correlation Analysis**: Heatmaps of inter-tier agreement
4. **Time Series**: Score trends across multiple assessment runs
5. **Cost Analysis**: API usage and processing time comparisons

#### Export Capabilities
- **CSV Data Export**: Raw scores and metrics for statistical software
- **PDF Reports**: Professional formatted assessment summaries
- **JSON Archives**: Complete project data for reproducibility
- **Chart Exports**: High-quality visualizations for presentations

### Research Insights Panel
- **Tier Effectiveness**: Which tier performs best for different assignment types
- **Provider Analysis**: Strengths and weaknesses of different LLM providers
- **Consistency Findings**: How assessment repetition affects reliability
- **Cost/Benefit Analysis**: Processing time vs. quality improvements

## Post-Processing and Validation

### Score Extraction and Validation
The application implements robust post-processing to ensure reliable final grades:

#### Score Parsing
1. **Multiple Pattern Detection**: Look for grades in various formats (A+, 85/100, 4.0/4.0)
2. **Rubric Summation**: Extract individual criterion scores and total separately  
3. **Cross-Validation**: Compare LLM-reported total with sum of parts
4. **Confidence Scoring**: Rate the reliability of extracted grades

#### Validation Rules
```typescript
interface ValidationResult {
  isValid: boolean;
  confidence: number; // 0-1 scale
  issues: ValidationIssue[];
  extractedGrade: string;
  calculatedTotal: number;
  rubricBreakdown: RubricScore[];
}

interface ValidationIssue {
  type: 'GRADE_MISMATCH' | 'MISSING_RUBRIC_SCORE' | 'CALCULATION_ERROR';
  severity: 'WARNING' | 'ERROR';
  description: string;
  suggestedFix?: string;
}
```

#### Automated Corrections
- **Grade Normalization**: Convert all grades to consistent scale
- **Total Recalculation**: Use rubric scores as authoritative source
- **Missing Score Interpolation**: Estimate missing rubric scores when possible
- **Outlier Detection**: Flag unusually high/low scores for manual review

## Technical Implementation

### Technology Stack
- **Frontend**: React 18, TypeScript 5, TailwindCSS
- **Desktop Framework**: Tauri 2.0
- **Backend**: Rust with Tokio async runtime
- **Database**: SQLite with migrations
- **Charts**: Recharts/D3.js for visualizations
- **File Processing**: Rust crates for PDF/DOCX parsing

### Performance Requirements
- **Startup Time**: < 3 seconds to ready state
- **File Import**: Process 100 submissions in < 30 seconds
- **Grading Throughput**: Limited by LLM API rate limits
- **Memory Usage**: < 500MB for typical project (50 submissions)
- **Disk Usage**: ~2MB per submission including cache

### Security Considerations
- **Local Storage Only**: No cloud storage or remote databases
- **API Key Management**: Secure storage with encryption at rest
- **File Validation**: Malware scanning and content validation
- **Audit Logging**: Complete operation history for reproducibility

### Extensibility Points
- **Custom LLM Providers**: Plugin architecture for new APIs
- **Analysis Integrations**: Configurable microservice endpoints  
- **Export Formats**: Pluggable report generators
- **Rubric Templates**: Community template sharing (future)

## Development Roadmap

### Phase 1: Core Implementation (Months 1-3)
- Basic three-tier grading system
- File management and project structure
- Primary LLM provider integrations
- DocumentLens API integration

### Phase 2: Analytics and Comparison (Months 4-5)  
- Comprehensive dashboard implementation
- Statistical analysis tools
- Multiple assessment capabilities
- Export and reporting features

### Phase 3: Advanced Features (Months 6-7)
- Additional LLM providers (Ollama, Google, custom)
- Advanced post-processing and validation
- Performance optimizations
- Enhanced user experience features

### Phase 4: Research Tools (Months 8-9)
- Advanced statistical analysis
- Research study templates
- Batch processing capabilities
- Academic publication export formats

---

This specification provides a comprehensive foundation for building a research-grade AI assessment tool that balances practical utility with rigorous analytical capabilities. The improved workflow addresses current pain points while enabling sophisticated comparative studies of AI grading approaches.