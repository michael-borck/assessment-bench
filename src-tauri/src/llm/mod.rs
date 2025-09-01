use anyhow::Result;
use serde::{Deserialize, Serialize};

pub mod provider;
pub mod openai;

pub use provider::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMRequest {
    pub prompt: String,
    pub system_prompt: Option<String>,
    pub temperature: f32,
    pub max_tokens: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMResponse {
    pub content: String,
    pub tokens_used: Option<u32>,
    pub model: String,
}

#[async_trait::async_trait]
pub trait LLMProvider: Send + Sync {
    async fn generate(&self, request: LLMRequest) -> Result<LLMResponse>;
    fn model_name(&self) -> String;
    fn provider_type(&self) -> String;
}