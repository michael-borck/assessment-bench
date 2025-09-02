use super::LLMProvider;
use crate::db::models::LLMProviderConfig;
use anyhow::Result;

pub struct ProviderFactory;

impl ProviderFactory {
    pub fn create_provider(
        provider_type: &str,
        config_json: &str,
    ) -> Result<Box<dyn LLMProvider>> {
        let config: LLMProviderConfig = serde_json::from_str(config_json)?;
        
        match provider_type {
            "openai" => {
                let provider = super::openai::OpenAIProvider::new(&config)?;
                Ok(Box::new(provider))
            }
            "anthropic" => {
                Err(anyhow::anyhow!("Anthropic provider not yet implemented"))
            }
            "google" => {
                Err(anyhow::anyhow!("Google provider not yet implemented"))
            }
            "ollama" => {
                Err(anyhow::anyhow!("Ollama provider not yet implemented"))
            }
            "custom" => {
                Err(anyhow::anyhow!("Custom provider not yet implemented"))
            }
            _ => Err(anyhow::anyhow!("Unknown provider type: {}", provider_type)),
        }
    }

    pub fn validate_config(
        provider_type: &str,
        config_json: &str,
    ) -> Result<LLMProviderConfig> {
        let config: LLMProviderConfig = serde_json::from_str(config_json)?;
        
        match provider_type {
            "openai" => {
                if config.api_key.is_none() {
                    return Err(anyhow::anyhow!("OpenAI API key is required"));
                }
                if config.model.is_empty() {
                    return Err(anyhow::anyhow!("Model name is required"));
                }
            }
            "anthropic" => {
                if config.api_key.is_none() {
                    return Err(anyhow::anyhow!("Anthropic API key is required"));
                }
            }
            "ollama" => {
                if config.base_url.is_none() {
                    return Err(anyhow::anyhow!("Ollama base URL is required"));
                }
            }
            _ => {}
        }
        
        Ok(config)
    }

    pub fn get_supported_providers() -> Vec<&'static str> {
        vec!["openai", "anthropic", "google", "ollama", "custom"]
    }

    pub fn get_default_config(provider_type: &str) -> Result<LLMProviderConfig> {
        match provider_type {
            "openai" => Ok(LLMProviderConfig {
                api_key: None,
                base_url: Some("https://api.openai.com/v1".to_string()),
                model: "gpt-4o-mini".to_string(),
                temperature: 0.1,
                max_tokens: Some(2000),
            }),
            "anthropic" => Ok(LLMProviderConfig {
                api_key: None,
                base_url: Some("https://api.anthropic.com/v1".to_string()),
                model: "claude-3-haiku-20240307".to_string(),
                temperature: 0.1,
                max_tokens: Some(2000),
            }),
            "ollama" => Ok(LLMProviderConfig {
                api_key: None,
                base_url: Some("http://localhost:11434".to_string()),
                model: "llama3.1".to_string(),
                temperature: 0.1,
                max_tokens: Some(2000),
            }),
            _ => Err(anyhow::anyhow!("Unknown provider type: {}", provider_type)),
        }
    }
}