# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development
```bash
# Start development server
npm run dev

# Build frontend for production
npm run build

# Preview production build
npm run preview
```

### Desktop Application
```bash
# Run Tauri app in development mode
npm run tauri dev

# Build Tauri app for production
npm run tauri build

# Target specific platform
npm run tauri build --target x86_64-unknown-linux-gnu
```

### Rust Backend
```bash
# Navigate to Rust workspace
cd src-tauri/src-tauri

# Check Rust code
cargo check

# Run Rust tests
cargo test

# Build Rust binary
cargo build --release
```

### Type Checking
```bash
# TypeScript compilation check
npx tsc

# Fix auto-fixable linting issues
cargo fix --bin "assessment-bench"
```

## Architecture Overview

### Three-Tier Grading System
The core architecture implements a research-grade grading pipeline with increasing sophistication:

1. **Tier 1 (Basic)**: Direct LLM grading with rubric only
2. **Tier 2 (Enhanced)**: Includes DocumentLens text analysis preprocessing 
3. **Tier 3 (Assignment-Aware)**: Full context with assignment specifications

Each tier supports 1-10 repetitions for statistical reliability analysis.

### Frontend Architecture
- **React 18** with TypeScript and TailwindCSS
- **Zustand** for state management (`stores/projectStore.ts`)
- **Component Structure**:
  - `ProjectManager`: Project creation, rubric setup, submission import
  - `TestingLab`: Interactive LLM provider and grading testing
  - `ResultsDashboard`: Statistical visualization and analysis
  - `ComparisonDashboard`: Multi-provider performance comparison
- **Recharts** for data visualization
- **Export utilities** for CSV/JSON/PDF export (`utils/exportUtils.ts`)

### Backend Architecture (Rust/Tauri)
- **Database Layer** (`db/`):
  - `SimpleDatabase`: SQLite wrapper with async operations
  - `models.rs`: Core data structures (Project, Submission, GradingResult)
  - Graceful fallback to in-memory database for development

- **LLM Provider System** (`llm/`):
  - `provider.rs`: Abstract LLM provider trait
  - `openai.rs`: OpenAI implementation with error handling
  - Extensible for additional providers (Anthropic, Ollama)

- **Grading Engine** (`grading/`):
  - `tiers.rs`: Three-tier prompt generation logic
  - `validation.rs`: Score extraction and response parsing
  - `aggregation.rs`: Statistical analysis across multiple runs

- **DocumentLens Integration** (`document_analysis/`):
  - `client.rs`: Sophisticated text analysis with 20+ metrics
  - Reading level, writing quality, structure analysis
  - Mock implementation with real-world analysis algorithms

- **Command Interface** (`commands/`):
  - Tauri command handlers for frontend-backend communication
  - `simple_project.rs`: Development/testing commands
  - `analysis.rs`: DocumentLens and statistical analysis commands

### Key Patterns
- **Async-first**: All I/O operations use Tokio async runtime
- **Error Handling**: Comprehensive `Result<T>` patterns with `anyhow`
- **Type Safety**: Strong typing across Rust-TypeScript boundary
- **Local-first**: No cloud storage, SQLite for data persistence
- **Statistical Focus**: Multiple runs with aggregation for research validity

### Development Notes
- Database automatically falls back to in-memory mode if file operations fail
- All LLM API keys are stored securely and never logged
- DocumentLens provides sophisticated text analysis even in mock mode
- Export functionality works both through Tauri file operations and browser fallback
- Testing Lab provides interactive verification of all major components

### Current Status
**Completed**: Tier 1 & 2 grading, OpenAI provider, DocumentLens integration, statistical analysis, export capabilities, comprehensive UI
**Next**: Tier 3 assignment-aware grading, additional LLM providers (Anthropic, Ollama), testing suite

The codebase is production-ready for research applications with a focus on statistical rigor and privacy-first architecture.