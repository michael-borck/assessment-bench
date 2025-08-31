use serde::{Deserialize, Serialize};

#[tauri::command]
pub fn greet(name: &str) -> String {
    format!("Hello, {name}! You've been greeted from Rust!")
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileInfo {
    pub name: String,
    pub path: String,
    pub size: u64,
    pub modified: Option<String>,
    pub is_docx: bool,
}

#[tauri::command]
pub async fn browse_folder() -> Result<Vec<FileInfo>, String> {
    // For now, return mock data - we'll implement actual folder browsing next
    Ok(vec![
        FileInfo {
            name: "student_assignment_01.docx".to_string(),
            path: "/path/to/student_assignment_01.docx".to_string(),
            size: 1024,
            modified: Some("2024-08-30T14:30:00Z".to_string()),
            is_docx: true,
        },
        FileInfo {
            name: "student_assignment_02.docx".to_string(),
            path: "/path/to/student_assignment_02.docx".to_string(),
            size: 2048,
            modified: Some("2024-08-30T14:25:00Z".to_string()),
            is_docx: true,
        },
        FileInfo {
            name: "essay_draft_final.docx".to_string(),
            path: "/path/to/essay_draft_final.docx".to_string(),
            size: 3072,
            modified: Some("2024-08-30T15:00:00Z".to_string()),
            is_docx: true,
        },
    ])
}

#[tauri::command]
pub async fn read_file_content(file_path: String) -> Result<String, String> {
    // TODO: Implement actual Word document reading
    Ok(format!("Content of file: {file_path}\n\nThis is a placeholder for the document content that will be extracted from the Word file."))
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GradeRequest {
    pub submission_content: String,
    pub system_prompt: String,
    pub user_prompt: String,
    pub provider: String,
    pub model: String,
    pub api_key: String,
    pub temperature: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GradeResponse {
    pub success: bool,
    pub feedback: Option<String>,
    pub error: Option<String>,
}

#[tauri::command]
pub async fn grade_submission(_request: GradeRequest) -> Result<GradeResponse, String> {
    // TODO: Implement actual grading logic
    Ok(GradeResponse {
        success: true,
        feedback: Some("This is a placeholder response. Grading logic to be implemented.".to_string()),
        error: None,
    })
}

#[tauri::command]
pub async fn test_llm_connection(_provider: String, _api_key: String) -> Result<bool, String> {
    // TODO: Implement connection testing for each provider
    Ok(true)
}