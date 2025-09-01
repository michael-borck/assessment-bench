use crate::db::Database;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tauri::State;
use uuid::Uuid;

// Re-export all command modules
mod project;
mod provider;
mod document;
mod grading;
mod analysis;
mod simple_project;

pub use project::*;
pub use provider::*;
pub use document::*;
pub use grading::*;
pub use analysis::*;
pub use simple_project::*;

// Common types used across commands
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

// Helper function to handle database operations
pub async fn handle_db_operation<T, F, Fut>(
    db: &Database,
    operation: F,
) -> ApiResponse<T>
where
    F: FnOnce(&Database) -> Fut,
    Fut: std::future::Future<Output = Result<T>>,
{
    match operation(db).await {
        Ok(result) => ApiResponse::success(result),
        Err(e) => {
            log::error!("Database operation failed: {}", e);
            ApiResponse::error(e.to_string())
        }
    }
}