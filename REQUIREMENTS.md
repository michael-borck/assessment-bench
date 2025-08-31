# AI Assessor - Requirements Document

## Project Overview
AI Assessor is a desktop application for automatically grading student submissions using Large Language Models (LLMs). The application processes Word documents against customizable rubrics and grading criteria, generating detailed feedback for each submission.

## Core Functional Requirements

### 1. Document Processing
- **Input**: Support for Microsoft Word documents (.docx) containing student submissions
- **Batch Processing**: Grade single files or entire folders of submissions
- **Support Files**: Include rubrics, marking guides, and reference materials in the grading context
- **Output**: Generate graded assessments with detailed feedback
- **Export Formats**: Save results as Word documents, PDFs, or plain text

### 2. LLM Provider Support
The application must support multiple LLM providers with easy switching between them:

#### Supported Providers
- **OpenAI** (GPT-3.5, GPT-4, GPT-4 Turbo)
- **Anthropic** (Claude 3 Opus, Sonnet, Haiku)
- **Groq** (Llama, Mixtral, Gemma models)
- **Gemini** (Google's Gemini Pro, Gemini Flash, Gemini Ultra)
- **Ollama** (Local models with custom URL and optional bearer token)
- **OpenRouter** (Access to multiple models through single API)

#### Provider Configuration
- Store API keys securely (encrypted in local storage)
- Custom base URLs for self-hosted endpoints (Ollama)
- Bearer token authentication support
- Model selection per provider
- Temperature and max token settings
- Streaming response support

### 3. Grading Workflow

#### Pre-Grading Setup
1. Load system prompt (grading instructions and criteria)
2. Load user prompt (specific assignment context)
3. Load support files (rubrics, examples, guidelines)
4. Configure model and parameters

#### Grading Process
1. Select submissions to grade
2. Display real-time progress for batch grading
3. Stream AI responses as they generate
4. Save feedback automatically
5. Mark submissions as graded/ungraded

#### Post-Grading
1. Review and edit generated feedback
2. Export results in various formats
3. Track grading history
4. Generate summary reports

### 4. Prompt Management
- **System Prompts**: Define grading style, criteria, and behavior
- **User Prompts**: Specify assignment-specific instructions
- **Template Library**: Save and reuse common prompt templates
- **Variables**: Support for placeholders in prompts (e.g., {student_name}, {assignment_title})
- **Version Control**: Track changes to prompts over time

## Non-Functional Requirements

### 1. User Interface
- **Modern Design**: Clean, intuitive interface with dark/light theme support
- **Split Views**: Side-by-side display of submission and feedback
- **Code Editor**: Syntax-highlighted prompt editing (Monaco Editor)
- **Drag & Drop**: Support for file uploads via drag and drop
- **Responsive Layout**: Adaptable to different screen sizes
- **Keyboard Shortcuts**: Efficient navigation and actions
- **Progress Indicators**: Clear feedback during long operations

### 2. Performance
- **Fast Startup**: Application should load in under 2 seconds
- **Concurrent Processing**: Grade multiple submissions in parallel where possible
- **Memory Efficient**: Handle large documents without excessive memory usage
- **Responsive UI**: Interface remains responsive during API calls
- **Caching**: Cache API responses to avoid redundant calls

### 3. Security
- **API Key Encryption**: Secure storage of sensitive credentials
- **No Cloud Storage**: All data remains local to the user's machine
- **Secure Communication**: HTTPS for all API calls
- **Input Validation**: Sanitize all user inputs
- **Error Handling**: Graceful handling of API failures

### 4. Cross-Platform Support
- **Operating Systems**: Windows 10/11, macOS 11+, Ubuntu 20.04+
- **Architecture**: Support for x64 and ARM64 (Apple Silicon)
- **Package Size**: Installer under 20MB per platform
- **Auto-Updates**: Built-in update mechanism
- **Portable Mode**: Option to run without installation

### 5. Accessibility
- **Screen Reader Support**: Compatible with common screen readers
- **Keyboard Navigation**: Full functionality without mouse
- **High Contrast Mode**: Support for high contrast themes
- **Font Scaling**: Adjustable text size

## Technical Requirements

### Frontend (React + TypeScript)
- **Framework**: React 18+ with TypeScript
- **State Management**: Zustand for app state, React Query for API state
- **UI Components**: Shadcn/ui or Ant Design
- **Editor**: Monaco Editor for code editing
- **Styling**: Tailwind CSS for responsive design
- **Build Tool**: Vite for fast development

### Backend (Rust + Tauri)
- **Framework**: Tauri 2.0
- **Language**: Rust for performance and security
- **Document Processing**: Native libraries for Word document parsing
- **HTTP Client**: Reqwest for API calls
- **Async Runtime**: Tokio for concurrent operations
- **Configuration**: TOML/JSON for settings storage

### Data Storage
- **Configuration**: JSON file in app data directory
- **Prompts**: Plain text files with metadata
- **History**: SQLite database for grading history
- **Cache**: Temporary directory for API response caching

## Feature Priorities

### Phase 1 - MVP (Core Functionality)
1. Basic UI with file browser and text displays
2. OpenAI provider support only
3. Single file grading
4. Simple prompt editing
5. Save feedback as text files

### Phase 2 - Multi-Provider Support
1. Add Anthropic, Groq, OpenRouter providers
2. Provider switching UI
3. Model selection per provider
4. Ollama local model support
5. Streaming responses

### Phase 3 - Enhanced Features
1. Batch grading with progress tracking
2. Monaco editor integration
3. Template library
4. Export to Word/PDF
5. Grading history

### Phase 4 - Polish
1. Auto-updates
2. Dark/light themes
3. Keyboard shortcuts
4. Advanced prompt variables
5. Summary reports

## Migration from Python Version

### Features to Preserve
- Core grading workflow
- Prompt structure and examples
- Support file inclusion
- Configuration options
- Output format

### Features to Improve
- **UI/UX**: Modern, responsive interface replacing Tkinter
- **Performance**: Faster processing with Rust backend
- **Distribution**: Smaller installers without Python runtime
- **Provider Support**: Multiple LLM providers vs OpenAI-only
- **Real-time Feedback**: Streaming responses vs waiting for completion

### Features to Add
- Multi-provider LLM support
- Streaming responses
- Template library
- Export options
- Auto-updates
- Theme support
- Keyboard shortcuts
- Grading history

## Success Criteria
1. Successfully grade Word documents using multiple LLM providers
2. Installer size under 20MB per platform
3. Application startup under 2 seconds
4. Intuitive UI requiring minimal training
5. Reliable auto-update mechanism
6. Support for offline operation with local models (Ollama)

## Constraints and Assumptions
- Users have their own API keys for cloud providers
- Internet connection required for cloud providers
- Local storage available for configuration and history
- Word documents are the primary input format
- English language interface (internationalization in future)