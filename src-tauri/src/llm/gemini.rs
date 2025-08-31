use async_trait::async_trait;
use super::{LLMProvider, LLMConfig, Message};

pub struct GeminiProvider {
    // TODO: HTTP client will be used for making API calls to Google Gemini in Phase 2
    // Keeping it as a field ensures consistent client reuse across requests
    #[allow(dead_code)]
    client: reqwest::Client,
}

impl GeminiProvider {
    // TODO: Constructor will be called from provider.rs when Gemini is selected
    // Currently unused but required for provider instantiation in Phase 2
    #[allow(dead_code)]
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl LLMProvider for GeminiProvider {
    async fn complete(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<String, Box<dyn std::error::Error>> {
        // TODO: Implement Google Gemini API call
        // API endpoint: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
        Ok("Gemini response placeholder".to_string())
    }
    
    async fn stream(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<Box<dyn futures::Stream<Item = Result<String, Box<dyn std::error::Error>>> + Unpin>, Box<dyn std::error::Error>> {
        // TODO: Implement streaming with Gemini API
        Err("Streaming not yet implemented".into())
    }
    
    async fn test_connection(&self, _config: &LLMConfig) -> Result<bool, Box<dyn std::error::Error>> {
        // TODO: Test API connection with Gemini
        Ok(true)
    }
}