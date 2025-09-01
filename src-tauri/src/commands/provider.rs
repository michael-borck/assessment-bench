use super::{handle_db_operation, ApiResponse};
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

    let response = handle_db_operation(&db, |db| async move {
        let provider = db.add_provider(provider).await?;
        Ok(provider)
    }).await;

    Ok(response)
}

#[command]
pub async fn get_providers(
    db: State<'_, Database>,
) -> Result<ApiResponse<Vec<LLMProvider>>, String> {
    let response = handle_db_operation(&db, |db| async move {
        let providers = db.get_providers().await?;
        Ok(providers)
    }).await;

    Ok(response)
}

#[command]
pub async fn update_provider(
    id: String,
    request: AddProviderRequest,
    db: State<'_, Database>,
) -> Result<ApiResponse<LLMProvider>, String> {
    // Delete old provider and create new one (simple update strategy)
    let response = handle_db_operation(&db, |db| async move {
        db.delete_provider(&id).await?;
        
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
        
        let provider = db.add_provider(provider).await?;
        Ok(provider)
    }).await;

    Ok(response)
}

#[command]
pub async fn delete_provider(
    id: String,
    db: State<'_, Database>,
) -> Result<ApiResponse<bool>, String> {
    let response = handle_db_operation(&db, |db| async move {
        let deleted = db.delete_provider(&id).await?;
        Ok(deleted)
    }).await;

    Ok(response)
}