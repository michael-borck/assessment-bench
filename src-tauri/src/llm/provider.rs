use super::LLMProvider;
use super::openai::OpenAIProvider;
use super::anthropic::AnthropicProvider;

pub enum Provider {
    OpenAI,
    Anthropic,
    Groq,
    Ollama,
    OpenRouter,
}

impl Provider {
    pub fn from_string(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "openai" => Some(Provider::OpenAI),
            "anthropic" => Some(Provider::Anthropic),
            "groq" => Some(Provider::Groq),
            "ollama" => Some(Provider::Ollama),
            "openrouter" => Some(Provider::OpenRouter),
            _ => None,
        }
    }
    
    pub fn get_provider(&self) -> Box<dyn LLMProvider> {
        match self {
            Provider::OpenAI => Box::new(OpenAIProvider::new()),
            Provider::Anthropic => Box::new(AnthropicProvider::new()),
            _ => Box::new(OpenAIProvider::new()), // Placeholder for now
        }
    }
}