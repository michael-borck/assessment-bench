use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct GradingSession {
    pub id: String,
    pub submission_path: String,
    pub system_prompt: String,
    pub user_prompt: String,
    pub support_files: Vec<String>,
    pub status: GradingStatus,
    pub result: Option<GradingResult>,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum GradingStatus {
    Pending,
    InProgress,
    Completed,
    Failed,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GradingResult {
    pub feedback: String,
    pub timestamp: String,
    pub model_used: String,
    pub provider_used: String,
}