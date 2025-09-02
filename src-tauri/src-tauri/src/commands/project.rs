use super::ApiResponse;
use crate::db::{models::Project, Database};
use serde::{Deserialize, Serialize};
use tauri::{command, State};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateProjectRequest {
    pub name: String,
    pub description: Option<String>,
    pub tiers_enabled: Vec<String>,
    pub repetitions: u32,
    pub document_lens_url: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProjectResponse {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub created_at: String,
    pub updated_at: String,
    pub config: serde_json::Value,
}

impl From<Project> for ProjectResponse {
    fn from(project: Project) -> Self {
        Self {
            id: project.id.to_string(),
            name: project.name,
            description: project.description,
            created_at: project.created_at.to_string(),
            updated_at: project.updated_at.to_string(),
            config: project.config,
        }
    }
}

#[command]
pub async fn create_project(
    request: CreateProjectRequest,
    db: State<'_, Database>,
) -> Result<ApiResponse<ProjectResponse>, String> {
    let config = serde_json::json!({
        "tiers_enabled": request.tiers_enabled,
        "repetitions": request.repetitions,
        "document_lens_url": request.document_lens_url,
        "providers": []
    });

    match db.create_project(request.name, request.description, config).await {
        Ok(project) => Ok(ApiResponse::success(ProjectResponse::from(project))),
        Err(e) => {
            log::error!("Failed to create project: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn get_projects(
    db: State<'_, Database>,
) -> Result<ApiResponse<Vec<ProjectResponse>>, String> {
    match db.get_projects().await {
        Ok(projects) => {
            let project_responses: Vec<ProjectResponse> = projects
                .into_iter()
                .map(ProjectResponse::from)
                .collect();
            Ok(ApiResponse::success(project_responses))
        }
        Err(e) => {
            log::error!("Failed to get projects: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn get_project(
    id: String,
    db: State<'_, Database>,
) -> Result<ApiResponse<ProjectResponse>, String> {
    let project_id = match Uuid::parse_str(&id) {
        Ok(id) => id,
        Err(_) => return Ok(ApiResponse::error("Invalid project ID format".to_string())),
    };

    match db.get_project(project_id).await {
        Ok(Some(project)) => Ok(ApiResponse::success(ProjectResponse::from(project))),
        Ok(None) => Ok(ApiResponse::error("Project not found".to_string())),
        Err(e) => {
            log::error!("Failed to get project: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn delete_project(
    id: String,
    db: State<'_, Database>,
) -> Result<ApiResponse<bool>, String> {
    let project_id = match Uuid::parse_str(&id) {
        Ok(id) => id,
        Err(_) => return Ok(ApiResponse::error("Invalid project ID format".to_string())),
    };

    match db.delete_project(project_id).await {
        Ok(deleted) => Ok(ApiResponse::success(deleted)),
        Err(e) => {
            log::error!("Failed to delete project: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}