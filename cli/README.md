# AI Assessor CLI - Batch Processing Tool

This command-line interface enables researchers and educators to perform automated grading operations on multiple student submissions using different AI workflows.

## Features

- **Dual Workflow Support**: Choose between Basic (LLM-only) and Enhanced (with document analysis)
- **Batch Processing**: Grade multiple submissions simultaneously
- **Multiple Output Formats**: JSON, CSV, or plain text results
- **Workflow Comparison**: Compare grading results between different approaches
- **Research-Grade Metrics**: Detailed analysis when using Enhanced workflow
- **Configurable Providers**: Support for OpenAI, Anthropic, and other LLM providers

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the AI Assessor application is running (for document analysis API)

## Usage

### Initialize Configuration

Generate a sample configuration file:
```bash
python batch_grader.py init --output my_config.json
```

### Grade Multiple Submissions

Grade all submissions in a directory:
```bash
python batch_grader.py grade \
  --directory /path/to/student/submissions \
  --config my_config.json \
  --output results
```

### Analyze Single Submission

Analyze a single file with enhanced workflow:
```bash
python batch_grader.py analyze \
  --file essay.txt \
  --workflow enhanced
```

### Compare Workflows

Compare Basic vs Enhanced workflows on the same submissions:
```bash
python batch_grader.py compare \
  --directory /path/to/submissions \
  --workflows basic,enhanced \
  --output comparison_study
```

## Configuration Options

The configuration file supports the following options:

```json
{
  "workflow": "enhanced",           // "basic" or "enhanced"
  "provider": "openai",            // LLM provider
  "model": "gpt-4-turbo",          // Model name
  "temperature": 0.7,              // Generation temperature
  "system_prompt": "...",          // System instructions
  "user_prompt": "...",            // User grading prompt
  "rubric_path": "./rubric.txt",   // Path to rubric file
  "marking_guide_path": "./guide.txt", // Path to marking guide
  "guidelines_path": "./guidelines.txt", // Path to guidelines
  "assignment_spec_path": "./spec.txt", // Optional assignment spec
  "document_analysis_url": "http://localhost:8001", // Analysis API URL
  "max_workers": 3,                // Parallel processing workers
  "output_format": "json"          // "json", "csv", or "txt"
}
```

## Support Files

The CLI requires the following support files:

### Required Files
- **Rubric** (`rubric.txt`): Grading criteria and performance descriptions
- **Marking Guide** (`marking_guide.txt`): Point allocations and sub-criteria
- **Guidelines** (`guidelines.txt`): Assignment instructions and requirements

### Optional Files
- **Assignment Specification** (`assignment_spec.txt`): Complete assignment document with context

## Workflows

### Basic Workflow
- Student submission + rubric + prompts → LLM → Grade + Feedback
- Fast processing, suitable for quick grading sessions

### Enhanced Workflow
- Student submission → Document Analysis API → Metrics
- Submission + Rubric + Metrics + Prompts → LLM → Grade + Feedback
- Provides research-grade analysis with detailed metrics

## Document Analysis Metrics

When using Enhanced workflow, the following metrics are automatically generated:

**Text Statistics**:
- Word count, paragraph count, sentence count
- Average words per sentence
- Average sentences per paragraph

**Readability Scores**:
- Flesch-Kincaid Grade Level
- Flesch Reading Ease Score
- Gunning Fog Index

**Academic Quality**:
- Academic vocabulary percentage
- Complex words percentage
- Passive voice usage

**Citations & Structure**:
- Citation count and format compliance
- Document structure analysis
- Grammar and spelling assessment

## Output Formats

### JSON Format
Detailed structured output with all metrics and metadata:
```json
[
  {
    "file_path": "/path/to/submission.txt",
    "student_name": "student_name",
    "workflow": "enhanced",
    "grade": "B+",
    "feedback": "Detailed feedback...",
    "metrics": { ... },
    "analysis_time": 2.3,
    "grading_time": 4.1
  }
]
```

### CSV Format
Tabular format suitable for spreadsheet analysis and statistical processing.

### Text Format
Human-readable format with grades and feedback for each student.

## Research Applications

This CLI tool is designed for research into AI-assisted assessment:

1. **Comparative Studies**: Compare different LLM approaches to grading
2. **Workflow Evaluation**: Assess the impact of document analysis on grading quality
3. **Consistency Analysis**: Measure grading consistency across multiple runs
4. **Performance Metrics**: Analyze processing time and throughput
5. **Quality Assessment**: Evaluate correlation between AI grades and human assessment

## Examples

### Research Study Setup
```bash
# Create configuration for the study
python batch_grader.py init --output study_config.json

# Grade with basic workflow
python batch_grader.py grade \
  --directory ./study_submissions \
  --config study_config.json \
  --workflow basic \
  --output basic_results

# Grade with enhanced workflow  
python batch_grader.py grade \
  --directory ./study_submissions \
  --config study_config.json \
  --workflow enhanced \
  --output enhanced_results

# Compare both approaches
python batch_grader.py compare \
  --directory ./study_submissions \
  --workflows basic,enhanced \
  --output workflow_comparison
```

### Quick Single File Analysis
```bash
python batch_grader.py analyze \
  --file student_essay.txt \
  --workflow enhanced
```

## Integration with Main Application

The CLI tool integrates with the main AI Assessor application by:

1. **Document Analysis API**: Uses the same analysis service for Enhanced workflow
2. **Support Files**: Can use the same rubric templates and support files
3. **Configuration**: Compatible configuration format for seamless workflow
4. **Results**: Can import CLI results back into the main application

## Error Handling

The tool includes comprehensive error handling:
- Missing support files are detected and reported
- Network errors for document analysis are gracefully handled
- File reading errors are logged with specific error messages
- Failed submissions are reported in the final summary

## Performance Considerations

- **Parallel Processing**: Configurable worker threads for concurrent grading
- **Rate Limiting**: Respects API rate limits for different LLM providers
- **Memory Management**: Efficient handling of large document collections
- **Caching**: Results are cached to avoid reprocessing on failures

## Troubleshooting

**Common Issues**:

1. **Document Analysis API Not Available**:
   - Ensure the main AI Assessor application is running
   - Check the `document_analysis_url` in configuration
   - Enhanced workflow will fall back to basic metrics

2. **Missing Support Files**:
   - Verify file paths in configuration
   - Ensure required files (rubric, marking guide, guidelines) exist

3. **LLM API Errors**:
   - Check API keys and provider configuration
   - Verify model names and availability
   - Monitor rate limits and quotas