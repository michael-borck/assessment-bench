use super::{LLMProvider, LLMRequest, LLMResponse};
use crate::db::models::{LLMProvider as DbLLMProvider, LLMProviderConfig};
use anyhow::Result;

pub struct ProviderFactory;

impl ProviderFactory {
    pub fn create_provider(config: &DbLLMProvider) -> Result<Box<dyn LLMProvider>> {
        match config.provider_type.as_str() {
            "openai" => {
                let provider = super::openai::OpenAIProvider::new(&config.config)?;
                Ok(Box::new(provider))
            }
            "anthropic" => {
                // TODO: Implement Anthropic provider
                Err(anyhow::anyhow!("Anthropic provider not yet implemented"))
            }
            "google" => {
                // TODO: Implement Google provider
                Err(anyhow::anyhow!("Google provider not yet implemented"))
            }
            "ollama" => {
                // TODO: Implement Ollama provider
                Err(anyhow::anyhow!("Ollama provider not yet implemented"))
            }
            "custom" => {
                // TODO: Implement Custom provider
                Err(anyhow::anyhow!("Custom provider not yet implemented"))
            }
            _ => Err(anyhow::anyhow!("Unknown provider type: {}", config.provider_type)),
        }
    }
}