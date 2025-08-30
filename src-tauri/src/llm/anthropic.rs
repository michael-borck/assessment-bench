use async_trait::async_trait;
use super::{LLMProvider, LLMConfig, Message};

pub struct AnthropicProvider {
    client: reqwest::Client,
}

impl AnthropicProvider {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl LLMProvider for AnthropicProvider {
    async fn complete(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<String, Box<dyn std::error::Error>> {
        // TODO: Implement Anthropic API call
        Ok("Anthropic response placeholder".to_string())
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