use super::{LLMProvider, LLMRequest, LLMResponse};
use crate::db::models::LLMProviderConfig;
use anyhow::Result;
use reqwest::Client;
use serde::{Deserialize, Serialize};

pub struct OpenAIProvider {
    client: Client,
    api_key: String,
    base_url: String,
    model: String,
}

#[derive(Serialize)]
struct OpenAIRequest {
    model: String,
    messages: Vec<OpenAIMessage>,
    temperature: f32,
    #[serde(skip_serializing_if = "Option::is_none")]
    max_tokens: Option<u32>,
}

#[derive(Serialize)]
struct OpenAIMessage {
    role: String,
    content: String,
}

#[derive(Deserialize)]
struct OpenAIResponse {
    choices: Vec<OpenAIChoice>,
    usage: Option<OpenAIUsage>,
}

#[derive(Deserialize)]
struct OpenAIChoice {
    message: OpenAIMessage,
}

#[derive(Deserialize)]
struct OpenAIUsage {
    total_tokens: u32,
}

impl OpenAIProvider {
    pub fn new(config: &LLMProviderConfig) -> Result<Self> {
        let api_key = config.api_key
            .as_ref()
            .ok_or_else(|| anyhow::anyhow!("OpenAI API key is required"))?
            .clone();

        let base_url = config.base_url
            .as_ref()
            .unwrap_or(&"https://api.openai.com/v1".to_string())
            .clone();

        Ok(Self {
            client: Client::new(),
            api_key,
            base_url,
            model: config.model.clone(),
        })
    }
}

#[async_trait::async_trait]
impl LLMProvider for OpenAIProvider {
    async fn generate(&self, request: LLMRequest) -> Result<LLMResponse> {
        let mut messages = vec![];

        // Add system prompt if provided
        if let Some(system_prompt) = &request.system_prompt {
            messages.push(OpenAIMessage {
                role: "system".to_string(),
                content: system_prompt.clone(),
            });
        }

        // Add user prompt
        messages.push(OpenAIMessage {
            role: "user".to_string(),
            content: request.prompt,
        });

        let openai_request = OpenAIRequest {
            model: self.model.clone(),
            messages,
            temperature: request.temperature,
            max_tokens: request.max_tokens,
        };

        let response = self
            .client
            .post(&format!("{}/chat/completions", self.base_url))
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&openai_request)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await.unwrap_or_default();
            return Err(anyhow::anyhow!("OpenAI API error: {}", error_text));
        }

        let openai_response: OpenAIResponse = response.json().await?;

        let choice = openai_response.choices
            .first()
            .ok_or_else(|| anyhow::anyhow!("No response from OpenAI"))?;

        Ok(LLMResponse {
            content: choice.message.content.clone(),
            tokens_used: openai_response.usage.map(|u| u.total_tokens),
            model: self.model.clone(),
        })
    }

    fn model_name(&self) -> String {
        self.model.clone()
    }

    fn provider_type(&self) -> String {
        "openai".to_string()
    }
}