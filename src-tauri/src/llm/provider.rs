use super::LLMProvider;
use super::openai::OpenAIProvider;
use super::anthropic::AnthropicProvider;
use super::gemini::GeminiProvider;

// TODO: This Provider enum will be used when implementing the actual provider selection
// logic in Phase 2. It allows dynamic selection of LLM providers based on user configuration.
// Currently unused but essential for the multi-provider architecture.
#[allow(dead_code)]
pub enum Provider {
    OpenAI,
    Anthropic,
    Groq,
    Gemini,
    Ollama,
    OpenRouter,
}

impl Provider {
    // TODO: Will be used when parsing provider types from frontend configuration
    // This converts string provider names to typed enum values for runtime selection
    #[allow(dead_code)]
    pub fn from_string(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "openai" => Some(Provider::OpenAI),
            "anthropic" => Some(Provider::Anthropic),
            "groq" => Some(Provider::Groq),
            "gemini" => Some(Provider::Gemini),
            "ollama" => Some(Provider::Ollama),
            "openrouter" => Some(Provider::OpenRouter),
            _ => None,
        }
    }
    
    // TODO: Will be used to instantiate the correct provider implementation
    // based on user's selected provider in the UI
    #[allow(dead_code)]
    pub fn get_provider(&self) -> Box<dyn LLMProvider> {
        match self {
            Provider::OpenAI => Box::new(OpenAIProvider::new()),
            Provider::Anthropic => Box::new(AnthropicProvider::new()),
            Provider::Gemini => Box::new(GeminiProvider::new()),
            _ => Box::new(OpenAIProvider::new()), // Placeholder for Groq, Ollama, OpenRouter
        }
    }
}