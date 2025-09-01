# AssessmentBench

> Research-grade benchmarking tool for AI-powered grading systems

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tauri](https://img.shields.io/badge/Tauri-2.0-blue.svg)](https://tauri.app/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![Rust](https://img.shields.io/badge/Rust-2021-orange.svg)](https://www.rust-lang.org/)

AssessmentBench is a desktop application designed for educators and researchers to systematically evaluate and compare AI-powered grading approaches. It implements a sophisticated **Three-Tier Grading System** with comprehensive analysis capabilities, statistical aggregation, and comparative assessment tools.

## 🎯 Key Features

### 🔬 **Research-First Design**
- **Three-Tier Grading System**: Basic LLM → Enhanced LLM → Assignment-Aware
- **Multiple Assessment Runs**: 1-10 repetitions with statistical aggregation
- **Consistency Analysis**: Standard deviation, confidence intervals, reliability scores
- **Provider Comparison**: OpenAI, Anthropic, Google, Ollama, and custom endpoints

### 📊 **Statistical Analysis**
- Mean, median, and standard deviation calculations
- Coefficient of variation for consistency measurement
- Score distribution visualization
- Inter-tier correlation analysis
- Convergence analysis across multiple runs

### 🔒 **Complete Data Privacy**
- **Local-first architecture** - all data stays on your machine
- No cloud storage or external data transmission
- SQLite database for complete control
- Secure API key storage with encryption

### 🎓 **Educational Focus**
- Rubric-based assessment with customizable criteria
- Assignment specification integration
- DocumentLens API integration for text analysis
- Professional reporting and export capabilities

## 🏗️ Architecture

### **Technology Stack**
- **Frontend**: React 18, TypeScript, TailwindCSS
- **Desktop Framework**: Tauri 2.0
- **Backend**: Rust with Tokio async runtime
- **Database**: SQLite with sqlx
- **Document Processing**: PDF-extract, DOCX-rs
- **Visualization**: Recharts for statistical charts

### **Three-Tier Grading System**

#### **Tier 1: Basic LLM**
```
Essay + Rubric → LLM → Grade + Feedback
```
- Direct submission to LLM with rubric
- Fastest processing time
- Baseline for comparison studies

#### **Tier 2: Enhanced LLM**
```
Essay + Analysis + Rubric → LLM → Grade + Feedback
```
- DocumentLens preprocessing for objective metrics
- Readability, writing quality, word analysis
- Enhanced context for subjective assessment

#### **Tier 3: Assignment-Aware**
```
Essay + Analysis + Rubric + Assignment Spec → LLM → Grade + Feedback
```
- Full context awareness
- Assignment-specific criteria integration
- Learning objective alignment

## 🚀 Getting Started

### **Prerequisites**
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Rust](https://rustup.rs/) (latest stable)
- [Tauri CLI](https://tauri.app/v1/guides/getting-started/prerequisites)

### **Installation**
```bash
# Clone the repository
git clone https://github.com/michael-borck/assessment-bench.git
cd assessment-bench

# Install Node.js dependencies
npm install

# Install Tauri CLI (if not already installed)
npm install -g @tauri-apps/cli

# Development build
npm run tauri dev

# Production build
npm run tauri build
```

### **Quick Start**
1. **Create a Project**: Set up your assessment project with rubrics and submissions
2. **Configure Providers**: Add your LLM API keys (OpenAI, Anthropic, etc.)
3. **Import Submissions**: Drag and drop student essays (PDF, DOCX, TXT)
4. **Run Assessments**: Execute grading across multiple tiers and repetitions
5. **Analyze Results**: Compare tiers, analyze consistency, export findings

## 📖 Documentation

- **[Complete Specification](./docs/SPECIFICATION.md)** - Detailed technical specification
- **[API Documentation](./docs/API.md)** - Backend API reference *(coming soon)*
- **[User Guide](./docs/USER_GUIDE.md)** - Step-by-step usage guide *(coming soon)*
- **[Development Guide](./docs/DEVELOPMENT.md)** - Contributing and development setup *(coming soon)*

## 🔬 Research Applications

AssessmentBench enables systematic research into AI grading approaches:

### **Research Questions**
- Does assignment specification improve grading accuracy?
- Which tier provides the most consistent results?
- How does preprocessing affect different LLM models?
- What's the optimal cost/benefit ratio for each tier?

### **Use Cases**
- **Academic Research**: Systematic evaluation of AI grading approaches
- **Educational Technology**: Testing and validating grading systems
- **Institutional Assessment**: Comparing AI tools for adoption decisions
- **Quality Assurance**: Ensuring consistent grading across large cohorts

## 🛠️ Current Status

**🚧 Under Active Development**

### **✅ Completed**
- [x] Project foundation and architecture
- [x] Three-tier grading system design
- [x] Database schema and migrations
- [x] LLM provider abstraction layer
- [x] React UI framework with TailwindCSS
- [x] Document processing framework

### **🔄 In Progress**
- [ ] SQLite database integration and testing
- [ ] OpenAI provider implementation
- [ ] Basic grading engine (Tier 1)
- [ ] Multiple assessment runs with aggregation

### **📋 Upcoming**
- [ ] DocumentLens API integration (Tier 2)
- [ ] Assignment-aware grading (Tier 3)
- [ ] Statistical visualization dashboard
- [ ] Export and reporting capabilities

## 🤝 Contributing

We welcome contributions! This project follows research-grade development practices:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### **Development Setup**
```bash
# Install dependencies
npm install

# Run in development mode
npm run tauri dev

# Run tests (when available)
npm test
cargo test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DocumentLens API** for advanced text analysis capabilities
- **Tauri** for the excellent cross-platform framework
- **OpenAI, Anthropic, Google** for LLM API access
- **Research Community** for inspiration and methodology guidance

## 📬 Contact

**Michael Borck** - [@michael-borck](https://github.com/michael-borck)

**Project Repository**: [https://github.com/michael-borck/assessment-bench](https://github.com/michael-borck/assessment-bench)

---

**Built for researchers, by researchers** 🔬✨