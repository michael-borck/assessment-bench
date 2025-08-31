use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

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
pub async fn browse_folder(folder_path: String) -> Result<Vec<FileInfo>, String> {
    let path = Path::new(&folder_path);
    
    // Check if the path exists and is a directory
    if !path.exists() {
        return Err(format!("Path does not exist: {}", folder_path));
    }
    
    if !path.is_dir() {
        return Err(format!("Path is not a directory: {}", folder_path));
    }
    
    let mut files = Vec::new();
    
    // Read all files in the selected folder
    match fs::read_dir(&path) {
        Ok(entries) => {
            for entry in entries.filter_map(Result::ok) {
                let path = entry.path();
                
                // Only include .docx, .doc, .pdf, and .txt files
                if let Some(extension) = path.extension() {
                    let ext = extension.to_string_lossy().to_lowercase();
                    if ext == "docx" || ext == "doc" || ext == "pdf" || ext == "txt" {
                        if let Ok(metadata) = entry.metadata() {
                            let modified = metadata.modified()
                                .ok()
                                .and_then(|time| {
                                    time.duration_since(std::time::UNIX_EPOCH).ok()
                                })
                                .map(|duration| {
                                    let secs = duration.as_secs() as i64;
                                    chrono::DateTime::from_timestamp(secs, 0)
                                        .map(|dt| dt.to_rfc3339())
                                        .unwrap_or_default()
                                });
                            
                            files.push(FileInfo {
                                name: path.file_name()
                                    .unwrap_or_default()
                                    .to_string_lossy()
                                    .to_string(),
                                path: path.to_string_lossy().to_string(),
                                size: metadata.len(),
                                modified,
                                is_docx: ext == "docx",
                            });
                        }
                    }
                }
            }
            
            // Sort files by name
            files.sort_by(|a, b| a.name.cmp(&b.name));
            Ok(files)
        }
        Err(e) => Err(format!("Failed to read directory: {}", e))
    }
}

#[tauri::command]
pub async fn read_file_content(file_path: String) -> Result<String, String> {
    let path = Path::new(&file_path);
    
    // Check if file exists
    if !path.exists() {
        return Err(format!("File not found: {}", file_path));
    }
    
    // Get file extension
    let extension = path.extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.to_lowercase())
        .unwrap_or_default();
    
    match extension.as_str() {
        "txt" => {
            // Read text files directly
            fs::read_to_string(path)
                .map_err(|e| format!("Failed to read file: {}", e))
        }
        "docx" | "doc" => {
            // TODO: Implement Word document reading with docx-rs or similar library
            // For now, return a placeholder indicating the file type
            Ok(format!("[Word Document: {}]\n\nWord document parsing will be implemented in Phase 2.\nFile size: {} bytes", 
                file_path, 
                fs::metadata(path).map(|m| m.len()).unwrap_or(0)))
        }
        "pdf" => {
            // TODO: Implement PDF reading with pdf-extract or similar library
            Ok(format!("[PDF Document: {}]\n\nPDF parsing will be implemented in Phase 2.\nFile size: {} bytes", 
                file_path,
                fs::metadata(path).map(|m| m.len()).unwrap_or(0)))
        }
        _ => {
            Err(format!("Unsupported file type: {}", extension))
        }
    }
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