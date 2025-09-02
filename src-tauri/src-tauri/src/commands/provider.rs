use super::ApiResponse;
use crate::db::{models::LLMProvider, Database};
use serde::{Deserialize, Serialize};
use tauri::{command, State};

#[derive(Debug, Serialize, Deserialize)]
pub struct AddProviderRequest {
    pub name: String,
    pub provider_type: String,
    pub api_key: Option<String>,
    pub base_url: Option<String>,
    pub model: String,
    pub temperature: f32,
    pub max_tokens: Option<u32>,
}

#[command]
pub async fn add_provider(
    request: AddProviderRequest,
    db: State<'_, Database>,
) -> Result<ApiResponse<LLMProvider>, String> {
    let provider = LLMProvider {
        id: uuid::Uuid::new_v4().to_string(),
        name: request.name,
        provider_type: request.provider_type,
        config: crate::db::models::LLMProviderConfig {
            api_key: request.api_key,
            base_url: request.base_url,
            model: request.model,
            temperature: request.temperature,
            max_tokens: request.max_tokens,
        },
    };

    match db.add_provider(provider).await {
        Ok(provider) => Ok(ApiResponse::success(provider)),
        Err(e) => {
            log::error!("Failed to add provider: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn get_providers(
    db: State<'_, Database>,
) -> Result<ApiResponse<Vec<LLMProvider>>, String> {
    match db.get_providers().await {
        Ok(providers) => Ok(ApiResponse::success(providers)),
        Err(e) => {
            log::error!("Failed to get providers: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn update_provider(
    id: String,
    request: AddProviderRequest,
    db: State<'_, Database>,
) -> Result<ApiResponse<LLMProvider>, String> {
    // Delete old provider and create new one (simple update strategy)
    match db.delete_provider(&id).await {
        Ok(_) => {},
        Err(e) => {
            log::error!("Failed to delete provider: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    }
    
    let provider = LLMProvider {
        id,
        name: request.name,
        provider_type: request.provider_type,
        config: crate::db::models::LLMProviderConfig {
            api_key: request.api_key,
            base_url: request.base_url,
            model: request.model,
            temperature: request.temperature,
            max_tokens: request.max_tokens,
        },
    };
    
    match db.add_provider(provider).await {
        Ok(provider) => Ok(ApiResponse::success(provider)),
        Err(e) => {
            log::error!("Failed to add updated provider: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn delete_provider(
    id: String,
    db: State<'_, Database>,
) -> Result<ApiResponse<bool>, String> {
    match db.delete_provider(&id).await {
        Ok(deleted) => Ok(ApiResponse::success(deleted)),
        Err(e) => {
            log::error!("Failed to delete provider: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}