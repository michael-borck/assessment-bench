use super::{handle_db_operation, ApiResponse};
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

    let response = handle_db_operation(&db, |db| async move {
        let project = db.create_project(
            request.name,
            request.description,
            config,
        ).await?;
        Ok(ProjectResponse::from(project))
    }).await;

    Ok(response)
}

#[command]
pub async fn get_projects(
    db: State<'_, Database>,
) -> Result<ApiResponse<Vec<ProjectResponse>>, String> {
    let response = handle_db_operation(&db, |db| async move {
        let projects = db.get_projects().await?;
        let project_responses: Vec<ProjectResponse> = projects
            .into_iter()
            .map(ProjectResponse::from)
            .collect();
        Ok(project_responses)
    }).await;

    Ok(response)
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

    let response = handle_db_operation(&db, |db| async move {
        let project = db.get_project(project_id).await?;
        match project {
            Some(project) => Ok(ProjectResponse::from(project)),
            None => Err(anyhow::anyhow!("Project not found")),
        }
    }).await;

    Ok(response)
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

    let response = handle_db_operation(&db, |db| async move {
        let deleted = db.delete_project(project_id).await?;
        Ok(deleted)
    }).await;

    Ok(response)
}