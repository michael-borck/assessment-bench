use async_trait::async_trait;
use super::{LLMProvider, LLMConfig, Message};
use serde::{Deserialize, Serialize};

pub struct OpenAIProvider {
    client: reqwest::Client,
}

impl OpenAIProvider {
    pub fn new() -> Self {
        Self {
            client: reqwest::Client::new(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIMessage {
    role: String,
    content: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIRequest {
    model: String,
    messages: Vec<OpenAIMessage>,
    temperature: f32,
    max_tokens: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIChoice {
    message: OpenAIMessage,
    finish_reason: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIResponse {
    id: String,
    choices: Vec<OpenAIChoice>,
    usage: Option<OpenAIUsage>,
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIUsage {
    prompt_tokens: u32,
    completion_tokens: u32,
    total_tokens: u32,
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIError {
    error: OpenAIErrorDetails,
}

#[derive(Debug, Serialize, Deserialize)]
struct OpenAIErrorDetails {
    message: String,
    #[serde(rename = "type")]
    error_type: String,
    code: Option<String>,
}

#[async_trait]
impl LLMProvider for OpenAIProvider {
    async fn complete(&self, config: &LLMConfig, messages: Vec<Message>) -> Result<String, Box<dyn std::error::Error>> {
        let base_url = config.base_url.as_deref().unwrap_or("https://api.openai.com");
        let url = format!("{}/v1/chat/completions", base_url);
        
        let openai_messages: Vec<OpenAIMessage> = messages.into_iter().map(|m| OpenAIMessage {
            role: m.role,
            content: m.content,
        }).collect();
        
        let request_body = OpenAIRequest {
            model: config.model.clone(),
            messages: openai_messages,
            temperature: config.temperature,
            max_tokens: config.max_tokens,
        };
        
        let response = self.client
            .post(&url)
            .header("Authorization", format!("Bearer {}", config.api_key))
            .header("Content-Type", "application/json")
            .json(&request_body)
            .send()
            .await?;
        
        let status = response.status();
        if !status.is_success() {
            let error_text = response.text().await?;
            if let Ok(error_response) = serde_json::from_str::<OpenAIError>(&error_text) {
                return Err(format!("OpenAI API error: {}", error_response.error.message).into());
            } else {
                return Err(format!("OpenAI API error: HTTP {}", status).into());
            }
        }
        
        let response_body = response.text().await?;
        let openai_response: OpenAIResponse = serde_json::from_str(&response_body)?;
        
        if let Some(choice) = openai_response.choices.first() {
            Ok(choice.message.content.clone())
        } else {
            Err("No completion choices returned".into())
        }
    }
    
    async fn stream(&self, _config: &LLMConfig, _messages: Vec<Message>) -> Result<Box<dyn futures::Stream<Item = Result<String, Box<dyn std::error::Error>>> + Unpin>, Box<dyn std::error::Error>> {
        // Streaming implementation would be more complex and is not critical for the initial version
        Err("Streaming not yet implemented for OpenAI".into())
    }
    
    async fn test_connection(&self, config: &LLMConfig) -> Result<bool, Box<dyn std::error::Error>> {
        let base_url = config.base_url.as_deref().unwrap_or("https://api.openai.com");
        let url = format!("{}/v1/models", base_url);
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", config.api_key))
            .send()
            .await?;
        
        Ok(response.status().is_success())
    }
}