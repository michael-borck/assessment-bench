pub mod provider;
pub mod openai;
pub mod anthropic;

use async_trait::async_trait;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct LLMConfig {
    pub api_key: String,
    pub model: String,
    pub temperature: f32,
    pub max_tokens: Option<u32>,
    pub base_url: Option<String>,
}

#[async_trait]
pub trait LLMProvider: Send + Sync {
    async fn complete(&self, config: &LLMConfig, messages: Vec<Message>) -> Result<String, Box<dyn std::error::Error>>;
    async fn stream(&self, config: &LLMConfig, messages: Vec<Message>) -> Result<Box<dyn futures::Stream<Item = Result<String, Box<dyn std::error::Error>>> + Unpin>, Box<dyn std::error::Error>>;
    async fn test_connection(&self, config: &LLMConfig) -> Result<bool, Box<dyn std::error::Error>>;
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}