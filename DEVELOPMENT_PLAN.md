# AI Assessor - Comprehensive Enhancement Plan

## **Project Vision**
Transform AI Assessor from a basic grading tool into a comprehensive research platform with dual workflows, template systems, assignment specification integration, and both GUI/CLI interfaces.

---

## **Phase 1: Enhanced Support File System**
### 1.1 Rubric Template Library
- **Built-in Templates:**
  - Essay rubrics (argumentative, analytical, narrative, compare/contrast)
  - Technical writing (lab reports, research proposals, case studies)
  - Creative writing (poetry, short stories, creative essays)
  - Academic papers (literature reviews, research papers, thesis chapters)
  - Code assignments (programming projects, algorithm analysis)
- **Template Management:**
  - Browse and preview templates in UI
  - Load template as starting point, allow customization
  - Save custom rubrics as new templates
  - Import/export template collections

### 1.2 Assignment Specification Integration
- **File Support:** Add assignment specification as 4th support file type
- **Smart Parsing:** 
  - Auto-detect embedded rubrics in assignment docs
  - Extract learning objectives and requirements
  - Identify grading criteria and point allocations
- **Context Enhancement:**
  - Use assignment context in grading prompts
  - Check submission completeness against requirements
  - Align grading with stated learning objectives

---

## **Phase 2: Dual Workflow Architecture**
### 2.1 Workflow Selection System
- **Basic Workflow:** Essay + Rubric + Prompt → LLM
- **Enhanced Workflow:** Essay + Document Analysis + Rubric + Assignment Spec + Prompt → LLM
- **UI Integration:** 
  - Workflow toggle in grading interface
  - Clear visual indicators of active workflow
  - Progress tracking for analysis phase

### 2.2 Document Analysis API Integration
- **Configuration:** API endpoint, credentials, timeout settings
- **Analysis Pipeline:**
  - Flesch readability scores
  - Word counting and frequency analysis
  - Sentence/paragraph metrics and variety
  - N-gram generation for style analysis
  - Writing quality metrics (passive voice detection)
  - Reference extraction and citation analysis
  - Suspicious pattern detection for integrity
- **Results Integration:** Format analysis data for LLM consumption

---

## **Phase 3: Data Models & Architecture Updates**
### 3.1 Enhanced Data Structures
```typescript
// Support file types expansion
type SupportFileType = 'rubric' | 'marking_guide' | 'guidelines' | 'assignment_spec'

// Document analysis results
interface DocumentAnalysis {
  readability: FleschScores
  wordStats: WordAnalysis
  sentenceMetrics: SentenceAnalysis
  writingQuality: QualityMetrics
  citations: CitationAnalysis
  integrityFlags: SuspiciousPatterns
}

// Workflow configuration
interface WorkflowConfig {
  type: 'basic' | 'enhanced'
  includeAnalysis: boolean
  analysisApiUrl?: string
  selectedMetrics: string[]
}
```

### 3.2 Template System
```typescript
interface RubricTemplate {
  id: string
  name: string
  category: string
  description: string
  criteria: RubricCriterion[]
  totalPoints: number
  createdBy: 'system' | 'user'
}
```

---

## **Phase 4: CLI Interface Development**
### 4.1 Headless Processing Engine
- **Separate CLI Binary:** `ai-assessor-cli` command
- **Configuration:** JSON/YAML config files + command line args
- **Batch Processing:** Process entire directories of submissions
- **Progress Reporting:** Real-time progress with ETA estimates

### 4.2 CLI Commands
```bash
# Process single submission
ai-assessor-cli grade --essay essay.docx --rubric rubric.pdf --workflow enhanced

# Batch processing with multiple workflows/models
ai-assessor-cli batch \
  --essays ./submissions/ \
  --rubric ./grading/rubric.docx \
  --assignment ./grading/assignment-spec.pdf \
  --workflows basic,enhanced \
  --models gpt-4,claude-3-opus \
  --output ./results/ \
  --format json,csv

# Template operations
ai-assessor-cli templates list
ai-assessor-cli templates export --category essays --output ./my-templates/
ai-assessor-cli templates import --file ./shared-templates.json
```

### 4.3 Integration Features
- **JSON/CSV Output:** Research-friendly data formats
- **Python Integration:** Easy import into pandas/jupyter notebooks
- **Configuration Templates:** Shareable research setups
- **Reproducibility:** Version tracking and deterministic results

---

## **Phase 5: Research & Comparison Features**
### 5.1 Comparative Analysis
- **Side-by-side Results:** Basic vs Enhanced workflow comparison
- **Statistical Analysis:** Grade correlation, consistency metrics
- **Bias Detection:** Identify systematic differences between workflows
- **Model Comparison:** Compare results across different LLMs

### 5.2 Export & Reporting
- **Research Datasets:** Export for statistical analysis software
- **Visualization:** Grade distribution plots, correlation matrices
- **Academic Reports:** Publication-ready summary tables
- **Raw Data Export:** Complete audit trail for reproducibility

---

## **Phase 6: Advanced Features**
### 6.1 Batch Analytics
- **Class-level Statistics:** Grade distributions, common issues
- **Trend Analysis:** Improvement over time, recurring problems
- **Rubric Effectiveness:** Which criteria discriminate well
- **Model Performance:** Accuracy vs human grading (when available)

### 6.2 Integration Ecosystem
- **LMS Integration:** Export to Canvas, Blackboard, etc.
- **Research Tools:** Direct export to R, SPSS, Python
- **Institutional Deployment:** Multi-user, shared templates
- **API Service:** Web-based access for institutional use

---

## **Implementation Priority**
1. **Phase 1:** Enhanced support files (templates + assignment specs)
2. **Phase 2:** Dual workflow system with API integration
3. **Phase 3:** Data model updates and enhanced grading logic
4. **Phase 4:** CLI interface development
5. **Phase 5:** Research comparison features
6. **Phase 6:** Advanced analytics and integrations

---

## **Research Impact**
This architecture enables studies on:
- Impact of objective metrics on LLM grading accuracy
- Consistency across different LLM providers
- Effectiveness of different rubric structures
- Bias patterns in automated assessment
- Scalability of LLM-based grading systems

The tool becomes a platform for advancing research in automated assessment and LLM capabilities in educational contexts.

---

## **Current Status**
- ✅ **Phase 1.0:** Basic support file management implemented
- ⏳ **Phase 1.1:** Rubric template library (in progress)
- ⏳ **Phase 1.2:** Assignment specification integration (next)

## **Development Log**
- **2024-12-XX:** Enhanced support file system with rubric, marking guide, guidelines
- **2024-12-XX:** Started Phase 1.1 - Template system development