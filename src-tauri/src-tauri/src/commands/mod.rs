use serde::{Deserialize, Serialize};

// Re-export all command modules
mod project;
mod provider;
mod document;
mod grading;
mod analysis;
mod simple_project;

// Use specific imports to avoid naming conflicts
pub use project::{create_project, get_projects, get_project, delete_project};
pub use provider::{add_provider, get_providers, update_provider, delete_provider};
pub use document::{import_documents, get_submissions};
pub use grading::{start_grading, get_grading_status, get_results};
pub use analysis::{get_aggregated_results, export_results, analyze_document_with_lens, test_documentlens_integration};
pub use simple_project::{
    create_project_simple, list_projects_simple, delete_project_simple,
    add_provider_simple, list_providers_simple, test_llm_provider, 
    test_basic_grading, test_multiple_grading_runs
};

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