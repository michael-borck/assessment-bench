# AssessmentBench - Development Guide

This document provides guidance for developers working on AssessmentBench.

## 🏗️ Architecture Overview

AssessmentBench follows a modern desktop application architecture:

```
Frontend (React/TypeScript)
    ↓ Tauri Commands
Backend (Rust)
    ↓ Database Layer
SQLite Database
```

### **Directory Structure**

```
assessment-bench/
├── src/                    # React frontend
│   ├── components/        # UI components
│   ├── stores/           # State management (Zustand)
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities and helpers
│   ├── types/            # TypeScript definitions
│   └── styles/           # CSS and styling
├── src-tauri/            # Rust backend
│   ├── src/
│   │   ├── commands/     # Tauri command handlers
│   │   ├── db/          # Database operations
│   │   ├── llm/         # LLM provider implementations
│   │   ├── document/    # Document processing
│   │   ├── grading/     # Grading logic and validation
│   │   └── analysis/    # Statistical analysis
│   ├── migrations/      # Database migrations
│   └── icons/           # Application icons
├── docs/                # Documentation
└── public/              # Static assets
```

## 🛠️ Development Setup

### **Prerequisites**
- [Node.js](https://nodejs.org/) v18+
- [Rust](https://rustup.rs/) (latest stable)
- [Tauri CLI](https://tauri.app/v1/guides/getting-started/prerequisites)

### **Setup Steps**
```bash
# Clone the repository
git clone https://github.com/michael-borck/assessment-bench.git
cd assessment-bench

# Install dependencies
npm install

# Install Tauri CLI globally
npm install -g @tauri-apps/cli

# Run in development mode
npm run tauri dev
```

## 🧪 Testing

### **Frontend Testing**
```bash
# Run React tests (when implemented)
npm test
```

### **Backend Testing**
```bash
# Run Rust tests
cd src-tauri
cargo test
```

## 📦 Building

### **Development Build**
```bash
npm run tauri dev
```

### **Production Build**
```bash
npm run tauri build
```

Built applications will be in `src-tauri/target/release/bundle/`.

## 🔄 Development Workflow

### **Adding New Features**

1. **Database Changes**
   - Update `src-tauri/src/db/models.rs` for new data structures
   - Add migration in `src-tauri/src/db/migrations.rs`
   - Update database operations in `src-tauri/src/db/mod.rs`

2. **Backend API**
   - Add command handler in appropriate `src-tauri/src/commands/*.rs`
   - Update `src-tauri/src/main.rs` to register new commands
   - Implement business logic in relevant modules

3. **Frontend Integration**
   - Add TypeScript types in `src/types/index.ts`
   - Create React components in `src/components/`
   - Add state management with Zustand in `src/stores/`
   - Update UI as needed

### **Code Style**

**Rust**
- Follow standard Rust formatting (`cargo fmt`)
- Use `cargo clippy` for linting
- Document public APIs with doc comments

**TypeScript/React**
- Use TypeScript strict mode
- Follow React functional component patterns
- Use TailwindCSS for styling
- Prefer composition over inheritance

## 📊 Database Schema

The application uses SQLite with the following key tables:

- `projects` - Assessment projects
- `llm_providers` - LLM provider configurations
- `submissions` - Student submissions
- `grading_results` - Individual grading results
- `rubrics` - Grading rubrics

See `src-tauri/src/db/migrations.rs` for complete schema.

## 🔌 LLM Provider Integration

To add a new LLM provider:

1. **Implement the Provider**
   ```rust
   // src-tauri/src/llm/my_provider.rs
   pub struct MyProvider {
       // implementation
   }
   
   #[async_trait::async_trait]
   impl LLMProvider for MyProvider {
       // implement required methods
   }
   ```

2. **Register in Factory**
   ```rust
   // src-tauri/src/llm/provider.rs
   match config.provider_type.as_str() {
       "my_provider" => {
           let provider = MyProvider::new(&config.config)?;
           Ok(Box::new(provider))
       }
       // ... existing providers
   }
   ```

3. **Update Frontend Types**
   ```typescript
   // src/types/index.ts
   export type LLMProviderType = 'openai' | 'anthropic' | 'my_provider';
   ```

## 🐛 Debugging

### **Frontend Debugging**
- Use browser DevTools (Ctrl+Shift+I in development)
- React DevTools extension for component inspection
- Console logging with `console.log()` and `console.error()`

### **Backend Debugging**
- Use `log::debug!()`, `log::info!()`, `log::error!()` for logging
- Set `RUST_LOG=debug` environment variable for verbose logging
- Use `cargo run` instead of Tauri dev for pure backend testing

### **Common Issues**

1. **Database Connection Errors**
   - Check if SQLite file permissions are correct
   - Verify database path in configuration

2. **API Key Issues**
   - Ensure API keys are properly encrypted/decrypted
   - Check provider configuration format

3. **Build Errors**
   - Clear `node_modules` and `target` directories
   - Ensure all dependencies are correctly installed

## 📝 Contributing Guidelines

1. **Branch Naming**
   - `feature/description` for new features
   - `fix/description` for bug fixes
   - `docs/description` for documentation updates

2. **Commit Messages**
   - Use conventional commit format
   - Include clear, descriptive messages
   - Reference issues when applicable

3. **Pull Requests**
   - Ensure all tests pass
   - Update documentation as needed
   - Request review from maintainers

## 🚀 Release Process

1. **Version Updates**
   - Update `package.json` version
   - Update `Cargo.toml` version
   - Update `tauri.conf.json` version

2. **Build and Test**
   - Run full test suite
   - Create production builds for all platforms
   - Test critical functionality

3. **Release**
   - Create GitHub release with changelog
   - Attach build artifacts
   - Update documentation

## 📞 Support

For development questions and support:
- Create an issue on GitHub
- Check existing documentation
- Review code comments and examples

---

**Happy Coding!** 🚀