use async_trait::async_trait;
use super::{LLMProvider, LLMConfig, Message};

pub struct OpenAIProvider {
    // TODO: HTTP client will be used for making API calls to OpenAI in Phase 2
    // Keeping it as a field ensures consistent client reuse across requests
    #[allow(dead_code)]
    client: reqwest::Client,
}

impl OpenAIProvider {
    // TODO: Constructor will be called from provider.rs when OpenAI is selected
    // Currently unused but required for provider instantiation in Phase 2
    #[allow(dead_code)]
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl LLMProvider for OpenAIProvider {
    async fn complete(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<String, Box<dyn std::error::Error>> {
        // TODO: Implement OpenAI API call
        Ok("OpenAI response placeholder".to_string())
    }
    
    async fn stream(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<Box<dyn futures::Stream<Item = Result<String, Box<dyn std::error::Error>>> + Unpin>, Box<dyn std::error::Error>> {
        // TODO: Implement streaming
        Err("Streaming not yet implemented".into())
    }
    
    async fn test_connection(&self, _config: &LLMConfig) -> Result<bool, Box<dyn std::error::Error>> {
        // TODO: Test API connection
        Ok(true)
    }
}