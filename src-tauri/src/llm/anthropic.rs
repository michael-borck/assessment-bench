use async_trait::async_trait;
use super::{LLMProvider, LLMConfig, Message};
use serde::{Deserialize, Serialize};

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

#[derive(Debug, Serialize, Deserialize)]
struct AnthropicMessage {
    role: String,
    content: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnthropicRequest {
    model: String,
    max_tokens: u32,
    messages: Vec<AnthropicMessage>,
    temperature: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnthropicContent {
    #[serde(rename = "type")]
    content_type: String,
    text: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnthropicResponse {
    id: String,
    #[serde(rename = "type")]
    response_type: String,
    role: String,
    content: Vec<AnthropicContent>,
    model: String,
    stop_reason: Option<String>,
    usage: AnthropicUsage,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnthropicUsage {
    input_tokens: u32,
    output_tokens: u32,
}

#[derive(Debug, Serialize, Deserialize)]
struct AnthropicError {
    #[serde(rename = "type")]
    error_type: String,
    message: String,
}

#[async_trait]
impl LLMProvider for AnthropicProvider {
    async fn complete(&self, config: &LLMConfig, messages: Vec<Message>) -> Result<String, Box<dyn std::error::Error>> {
        let url = "https://api.anthropic.com/v1/messages";
        
        let anthropic_messages: Vec<AnthropicMessage> = messages.into_iter().map(|m| AnthropicMessage {
            role: m.role,
            content: m.content,
        }).collect();
        
        let request_body = AnthropicRequest {
            model: config.model.clone(),
            max_tokens: config.max_tokens.unwrap_or(4096),
            messages: anthropic_messages,
            temperature: Some(config.temperature),
        };
        
        let response = self.client
            .post(url)
            .header("x-api-key", &config.api_key)
            .header("Content-Type", "application/json")
            .header("anthropic-version", "2023-06-01")
            .json(&request_body)
            .send()
            .await?;
        
        let status = response.status();
        if !status.is_success() {
            let error_text = response.text().await?;
            if let Ok(error_response) = serde_json::from_str::<AnthropicError>(&error_text) {
                return Err(format!("Anthropic API error: {}", error_response.message).into());
            } else {
                return Err(format!("Anthropic API error: HTTP {}", status).into());
            }
        }
        
        let response_body = response.text().await?;
        let anthropic_response: AnthropicResponse = serde_json::from_str(&response_body)?;
        
        if let Some(content) = anthropic_response.content.first() {
            Ok(content.text.clone())
        } else {
            Err("No content returned".into())
        }
    }
    
    async fn stream(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<Box<dyn futures::Stream<Item = Result<String, Box<dyn std::error::Error>>> + Unpin>, Box<dyn std::error::Error>> {
        // Streaming implementation would be more complex and is not critical for the initial version
        Err("Streaming not yet implemented for Anthropic".into())
    }
    
    async fn test_connection(&self, config: &LLMConfig) -> Result<bool, Box<dyn std::error::Error>> {
        // Simple test with a minimal message
        let test_messages = vec![Message {
            role: "user".to_string(),
            content: "Hello".to_string(),
        }];
        
        match self.complete(config, test_messages).await {
            Ok(_) => Ok(true),
            Err(_) => Ok(false),
        }
    }
}