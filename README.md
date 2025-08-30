# AI Assessor

A modern desktop application for automatically grading student submissions using multiple Large Language Model providers.

## Features

- 🤖 **Multi-Provider LLM Support**: OpenAI, Anthropic, Groq, Ollama, OpenRouter
- 📄 **Document Processing**: Grade Word documents with customizable rubrics
- 🚀 **Modern UI**: Built with React and Tauri for a native desktop experience
- 💻 **Cross-Platform**: Windows, macOS, and Linux support
- 🔄 **Auto-Updates**: Built-in update mechanism
- 📦 **Small Installer**: ~10-15MB per platform

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: Rust + Tauri
- **UI Components**: Modern React components (to be added)
- **State Management**: Zustand (to be added)

## Development

### Prerequisites

- Node.js 18+
- Rust 1.70+
- Platform-specific dependencies:
  - **Windows**: Microsoft C++ Build Tools
  - **macOS**: Xcode Command Line Tools
  - **Linux**: `libgtk-3-dev`, `libwebkit2gtk-4.1-dev`, `libappindicator3-dev`

### Setup

1. Clone the repository:
```bash
git clone https://github.com/michael-borck/ai-assessor.git
cd ai-assessor
```

2. Install dependencies:
```bash
npm install
```

3. Run in development mode:
```bash
npm run tauri:dev
```

### Building

To create a production build:

```bash
npm run tauri:build
```

This will create platform-specific installers in `src-tauri/target/release/bundle/`.

## Project Structure

```
ai-assessor/
├── src/                    # React frontend
│   ├── components/         # UI components
│   ├── pages/             # Application pages
│   ├── hooks/             # Custom React hooks
│   ├── stores/            # State management
│   └── lib/               # Utilities
├── src-tauri/             # Rust backend
│   ├── src/
│   │   ├── commands/      # Tauri commands
│   │   ├── llm/          # LLM provider implementations
│   │   ├── grading/      # Core grading logic
│   │   └── document/     # Document processing
│   └── tauri.conf.json   # Tauri configuration
├── prompts/              # Prompt templates
└── package.json
```

## Roadmap

### Phase 1 - MVP
- [ ] Basic UI with file browser
- [ ] OpenAI provider support
- [ ] Single file grading
- [ ] Simple prompt editing

### Phase 2 - Multi-Provider
- [ ] Anthropic, Groq, OpenRouter support
- [ ] Ollama local model support
- [ ] Provider switching UI
- [ ] Streaming responses

### Phase 3 - Enhanced Features
- [ ] Batch grading
- [ ] Monaco editor integration
- [ ] Template library
- [ ] Export to Word/PDF

### Phase 4 - Polish
- [ ] Auto-updates
- [ ] Dark/light themes
- [ ] Keyboard shortcuts
- [ ] Grading history

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.