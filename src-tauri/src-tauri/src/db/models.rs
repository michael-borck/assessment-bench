use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: Uuid,
    pub name: String,
    pub description: Option<String>,
    pub config: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMProvider {
    pub id: String,
    pub name: String,
    pub provider_type: String, // 'openai', 'anthropic', 'google', 'ollama', 'custom'
    pub config: LLMProviderConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LLMProviderConfig {
    pub api_key: Option<String>,
    pub base_url: Option<String>,
    pub model: String,
    pub temperature: f32,
    pub max_tokens: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Submission {
    pub id: Uuid,
    pub project_id: Uuid,
    pub original_filename: String,
    pub file_hash: String,
    pub file_type: String, // 'pdf', 'docx', 'txt', 'md'
    pub word_count: u32,
    pub status: String, // 'pending', 'processing', 'processed', 'error'
    pub extracted_text: Option<String>,
    pub analysis_cache: Option<DocumentAnalysis>,
    pub imported_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentAnalysis {
    // Basic text metrics
    pub word_count: u32,
    pub sentence_count: u32,
    pub paragraph_count: u32,
    
    // Readability scores
    pub flesch_reading_ease: Option<f32>,
    pub flesch_kincaid_grade: Option<f32>,
    
    // Writing quality metrics
    pub passive_voice_percentage: Option<f32>,
    pub sentence_variety_score: Option<f32>,
    pub vocabulary_richness: Option<f32>,
    
    // Academic analysis (Tier 3)
    pub citations: Option<Vec<Citation>>,
    pub ai_detection_score: Option<f32>,
    pub plagiarism_indicators: Option<Vec<String>>,
    pub reference_integrity: Option<Vec<ReferenceCheck>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Citation {
    pub text: String,
    pub style: String,
    pub doi: Option<String>,
    pub url: Option<String>,
    pub verified: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReferenceCheck {
    pub citation: String,
    pub status: String, // 'valid', 'invalid', 'warning'
    pub message: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GradingResult {
    pub id: Uuid,
    pub submission_id: Uuid,
    pub provider_id: String,
    pub tier: String, // 'basic', 'enhanced', 'assignment-aware'
    pub run_number: u32,
    pub created_at: DateTime<Utc>,
    
    // Raw response
    pub raw_response: String,
    
    // Extracted scores
    pub overall_grade: Option<String>,
    pub total_points: Option<f32>,
    pub rubric_scores: Vec<RubricScore>,
    
    // Feedback
    pub summary_feedback: Option<String>,
    pub strengths: Vec<String>,
    pub improvements: Vec<String>,
    
    // Validation
    pub validation_result: ValidationResult,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RubricScore {
    pub criterion: String,
    pub points_awarded: f32,
    pub points_possible: f32,
    pub comments: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationResult {
    pub is_valid: bool,
    pub confidence: f32, // 0.0-1.0 scale
    pub issues: Vec<ValidationIssue>,
    pub extracted_grade: Option<String>,
    pub calculated_total: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationIssue {
    pub issue_type: String, // 'GRADE_MISMATCH', 'MISSING_RUBRIC_SCORE', 'CALCULATION_ERROR'
    pub severity: String,   // 'WARNING', 'ERROR'
    pub description: String,
    pub suggested_fix: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AggregatedResult {
    pub submission_id: Uuid,
    pub provider_id: String,
    pub tier: String,
    
    // Statistical measures
    pub mean_score: f32,
    pub median_score: f32,
    pub std_deviation: f32,
    pub coefficient_of_variation: f32,
    
    // Individual results
    pub individual_results: Vec<GradingResult>,
    
    // Aggregated feedback
    pub consensus_feedback: Option<String>,
    pub common_strengths: Vec<String>,
    pub common_improvements: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Rubric {
    pub id: Uuid,
    pub name: String,
    pub description: Option<String>,
    pub criteria: Vec<RubricCriterion>,
    pub total_points: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RubricCriterion {
    pub id: Uuid,
    pub name: String,
    pub description: String,
    pub points_possible: f32,
    pub levels: Option<Vec<RubricLevel>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RubricLevel {
    pub name: String,
    pub description: String,
    pub points: f32,
}