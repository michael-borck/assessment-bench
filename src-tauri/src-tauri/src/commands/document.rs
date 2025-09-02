use super::ApiResponse;
use crate::db::{models::Submission, Database};
use serde::{Deserialize, Serialize};
use tauri::{command, State};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct ImportDocumentsRequest {
    pub project_id: String,
    pub file_paths: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SubmissionResponse {
    pub id: String,
    pub original_filename: String,
    pub file_type: String,
    pub word_count: u32,
    pub status: String,
    pub imported_at: String,
}

impl From<Submission> for SubmissionResponse {
    fn from(submission: Submission) -> Self {
        Self {
            id: submission.id.to_string(),
            original_filename: submission.original_filename,
            file_type: submission.file_type,
            word_count: submission.word_count,
            status: submission.status,
            imported_at: submission.imported_at.to_string(),
        }
    }
}

#[command]
pub async fn import_documents(
    request: ImportDocumentsRequest,
    db: State<'_, Database>,
) -> Result<ApiResponse<Vec<SubmissionResponse>>, String> {
    let project_id = match Uuid::parse_str(&request.project_id) {
        Ok(id) => id,
        Err(_) => return Ok(ApiResponse::error("Invalid project ID format".to_string())),
    };

    let mut submissions = Vec::new();
    
    for file_path in request.file_paths {
        match crate::document::process_document(&file_path).await {
            Ok(submission_data) => {
                let submission = Submission {
                    id: Uuid::new_v4(),
                    project_id,
                    original_filename: submission_data.filename,
                    file_hash: submission_data.hash,
                    file_type: submission_data.file_type,
                    word_count: submission_data.word_count,
                    status: "processed".to_string(),
                    extracted_text: Some(submission_data.text),
                    analysis_cache: None,
                    imported_at: chrono::Utc::now(),
                };
                
                match db.create_submission(submission).await {
                    Ok(created_submission) => {
                        submissions.push(SubmissionResponse::from(created_submission));
                    }
                    Err(e) => {
                        log::error!("Failed to create submission: {}", e);
                        return Ok(ApiResponse::error(e.to_string()));
                    }
                }
            }
            Err(e) => {
                log::error!("Failed to process document {}: {}", file_path, e);
                // Continue with other documents
            }
        }
    }
    
    Ok(ApiResponse::success(submissions))
}

#[command]
pub async fn get_submissions(
    project_id: String,
    db: State<'_, Database>,
) -> Result<ApiResponse<Vec<SubmissionResponse>>, String> {
    let project_id = match Uuid::parse_str(&project_id) {
        Ok(id) => id,
        Err(_) => return Ok(ApiResponse::error("Invalid project ID format".to_string())),
    };

    match db.get_submissions(project_id).await {
        Ok(submissions) => {
            let submission_responses: Vec<SubmissionResponse> = submissions
                .into_iter()
                .map(SubmissionResponse::from)
                .collect();
            Ok(ApiResponse::success(submission_responses))
        }
        Err(e) => {
            log::error!("Failed to get submissions: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}