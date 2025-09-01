use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use crate::llm::{LLMConfig, Message};
use crate::llm::provider::Provider;

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
    pub rubric_content: Option<String>,
    pub marking_guide_content: Option<String>,
    pub guidelines_content: Option<String>,
    pub assignment_spec_content: Option<String>,
    pub system_prompt: String,
    pub user_prompt: String,
    pub provider: String,
    pub model: String,
    pub api_key: String,
    pub temperature: f32,
    pub max_tokens: Option<u32>,
    pub workflow: Option<String>,
    pub document_analysis: Option<DocumentAnalysis>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DocumentAnalysis {
    pub word_count: u32,
    pub reading_level: f32,
    pub citations: u32,
    pub grammar_score: f32,
    pub structure_score: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GradeResponse {
    pub success: bool,
    pub feedback: Option<String>,
    pub grade: Option<String>,
    pub error: Option<String>,
    pub processing_time: Option<f32>,
}

#[tauri::command]
pub async fn grade_submission(request: GradeRequest) -> Result<GradeResponse, String> {
    let start_time = std::time::Instant::now();
    
    // Parse provider
    let provider_enum = Provider::from_string(&request.provider)
        .ok_or_else(|| format!("Unsupported provider: {}", request.provider))?;
    
    // Create provider instance
    let provider = provider_enum.get_provider();
    
    // Build configuration
    let config = LLMConfig {
        api_key: request.api_key.clone(),
        model: request.model.clone(),
        temperature: request.temperature,
        max_tokens: request.max_tokens,
        base_url: None, // Could be configurable in the future
    };
    
    // Build the complete prompt with support files
    let mut prompt_parts = Vec::new();
    
    // Add system prompt
    if !request.system_prompt.is_empty() {
        prompt_parts.push(format!("SYSTEM INSTRUCTIONS:\n{}", request.system_prompt));
    }
    
    // Add support files
    if let Some(rubric) = &request.rubric_content {
        prompt_parts.push(format!("RUBRIC:\n{}", rubric));
    }
    
    if let Some(marking_guide) = &request.marking_guide_content {
        prompt_parts.push(format!("MARKING GUIDE:\n{}", marking_guide));
    }
    
    if let Some(guidelines) = &request.guidelines_content {
        prompt_parts.push(format!("ASSIGNMENT GUIDELINES:\n{}", guidelines));
    }
    
    if let Some(assignment_spec) = &request.assignment_spec_content {
        prompt_parts.push(format!("ASSIGNMENT SPECIFICATION:\n{}", assignment_spec));
    }
    
    // Add document analysis if provided (Enhanced workflow)
    if let Some(analysis) = &request.document_analysis {
        prompt_parts.push(format!(
            "DOCUMENT ANALYSIS:\n\
            - Word Count: {}\n\
            - Reading Level: {:.1}\n\
            - Citations Found: {}\n\
            - Grammar Score: {:.1}%\n\
            - Structure Score: {:.1}%\n\
            Please incorporate these metrics into your assessment.",
            analysis.word_count,
            analysis.reading_level,
            analysis.citations,
            analysis.grammar_score,
            analysis.structure_score
        ));
    }
    
    // Add submission content
    prompt_parts.push(format!("STUDENT SUBMISSION:\n{}", request.submission_content));
    
    // Add user prompt
    if !request.user_prompt.is_empty() {
        prompt_parts.push(format!("GRADING INSTRUCTIONS:\n{}", request.user_prompt));
    } else {
        prompt_parts.push("Please grade this submission according to the provided rubric and give detailed feedback.".to_string());
    }
    
    let full_prompt = prompt_parts.join("\n\n");
    
    // Create messages for the LLM
    let messages = vec![
        Message {
            role: "user".to_string(),
            content: full_prompt,
        }
    ];
    
    // Call the LLM
    match provider.complete(&config, messages).await {
        Ok(response) => {
            let processing_time = start_time.elapsed().as_secs_f32();
            
            // Simple grade extraction (look for common grade patterns)
            let grade = extract_grade(&response);
            
            Ok(GradeResponse {
                success: true,
                feedback: Some(response),
                grade,
                error: None,
                processing_time: Some(processing_time),
            })
        }
        Err(e) => {
            Ok(GradeResponse {
                success: false,
                feedback: None,
                grade: None,
                error: Some(e.to_string()),
                processing_time: Some(start_time.elapsed().as_secs_f32()),
            })
        }
    }
}

fn extract_grade(response: &str) -> Option<String> {
    // Simple grade extraction logic - look for common patterns
    let grade_patterns = [
        r"Grade:\s*([A-F][+-]?)",
        r"Overall Grade:\s*([A-F][+-]?)",
        r"Final Grade:\s*([A-F][+-]?)",
        r"Score:\s*([A-F][+-]?)",
        r"\b([A-F][+-]?)\s*(?:grade|Grade)",
        r"([A-F][+-]?)\s*/\s*100",
    ];
    
    for pattern in &grade_patterns {
        if let Ok(re) = regex::Regex::new(pattern) {
            if let Some(captures) = re.captures(response) {
                if let Some(grade_match) = captures.get(1) {
                    return Some(grade_match.as_str().to_string());
                }
            }
        }
    }
    
    None
}

#[tauri::command]
pub async fn test_llm_connection(provider_name: String, api_key: String, model: String) -> Result<bool, String> {
    // Parse provider
    let provider_enum = Provider::from_string(&provider_name)
        .ok_or_else(|| format!("Unsupported provider: {}", provider_name))?;
    
    // Create provider instance
    let provider = provider_enum.get_provider();
    
    // Build configuration
    let config = LLMConfig {
        api_key,
        model,
        temperature: 0.7,
        max_tokens: Some(10), // Minimal tokens for testing
        base_url: None,
    };
    
    // Test connection
    match provider.test_connection(&config).await {
        Ok(result) => Ok(result),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub async fn browse_support_files() -> Result<Vec<FileInfo>, String> {
    // TODO: This will need to be implemented with the proper dialog integration
    // For now, return empty to avoid compilation errors
    Ok(vec![])
}