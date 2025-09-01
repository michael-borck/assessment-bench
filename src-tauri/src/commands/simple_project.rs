// Simplified project management commands that work with SimpleDatabase
use crate::db::SimpleDatabase;
use serde::{Deserialize, Serialize};
use tauri::{command, State};

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateProjectRequest {
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimpleProjectResponse {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub error: Option<String>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    pub fn error(message: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(message),
        }
    }
}

#[command]
pub async fn create_project_simple(
    request: CreateProjectRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<SimpleProjectResponse>, String> {
    match db.create_project_simple(request.name.clone(), request.description.clone()).await {
        Ok(id) => {
            let response = SimpleProjectResponse {
                id,
                name: request.name,
                description: request.description,
            };
            Ok(ApiResponse::success(response))
        }
        Err(e) => {
            log::error!("Failed to create project: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn list_projects_simple(
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<Vec<SimpleProjectResponse>>, String> {
    match db.list_projects().await {
        Ok(projects) => {
            let responses: Vec<SimpleProjectResponse> = projects
                .into_iter()
                .map(|(id, name)| SimpleProjectResponse {
                    id,
                    name,
                    description: None, // Simplified for now
                })
                .collect();
            Ok(ApiResponse::success(responses))
        }
        Err(e) => {
            log::error!("Failed to list projects: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn delete_project_simple(
    id: String,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<bool>, String> {
    // For now, return success (actual deletion can be implemented later)
    log::info!("Delete project requested: {}", id);
    Ok(ApiResponse::success(true))
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateProviderRequest {
    pub name: String,
    pub provider_type: String,
    pub model: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimpleProviderResponse {
    pub id: String,
    pub name: String,
    pub provider_type: String,
}

#[command]
pub async fn add_provider_simple(
    request: CreateProviderRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<SimpleProviderResponse>, String> {
    match db.add_provider_simple(
        request.name.clone(),
        request.provider_type.clone(),
        request.model,
    ).await {
        Ok(id) => {
            let response = SimpleProviderResponse {
                id,
                name: request.name,
                provider_type: request.provider_type,
            };
            Ok(ApiResponse::success(response))
        }
        Err(e) => {
            log::error!("Failed to add provider: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn list_providers_simple(
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<Vec<SimpleProviderResponse>>, String> {
    match db.list_providers().await {
        Ok(providers) => {
            let responses: Vec<SimpleProviderResponse> = providers
                .into_iter()
                .map(|(id, name, provider_type)| SimpleProviderResponse {
                    id,
                    name,
                    provider_type,
                })
                .collect();
            Ok(ApiResponse::success(responses))
        }
        Err(e) => {
            log::error!("Failed to list providers: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}