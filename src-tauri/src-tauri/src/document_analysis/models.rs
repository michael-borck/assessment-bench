use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisRequest {
    pub text: String,
    pub analysis_type: AnalysisType,
    pub options: AnalysisOptions,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AnalysisType {
    #[serde(rename = "comprehensive")]
    Comprehensive,
    #[serde(rename = "academic")]
    Academic,
    #[serde(rename = "writing_quality")]
    WritingQuality,
    #[serde(rename = "readability")]
    Readability,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisOptions {
    pub include_grammar: bool,
    pub include_style: bool,
    pub include_structure: bool,
    pub include_content_analysis: bool,
    pub academic_level: Option<String>,
}

impl Default for AnalysisOptions {
    fn default() -> Self {
        Self {
            include_grammar: true,
            include_style: true,
            include_structure: true,
            include_content_analysis: true,
            academic_level: Some("undergraduate".to_string()),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentLensResponse {
    pub analysis_id: String,
    pub status: String,
    pub analysis: Option<super::DocumentAnalysis>,
    pub error_message: Option<String>,
    pub processing_time_ms: Option<u64>,
}

impl AnalysisRequest {
    pub fn new_academic(text: String) -> Self {
        Self {
            text,
            analysis_type: AnalysisType::Academic,
            options: AnalysisOptions::default(),
        }
    }

    pub fn new_comprehensive(text: String) -> Self {
        Self {
            text,
            analysis_type: AnalysisType::Comprehensive,
            options: AnalysisOptions::default(),
        }
    }
}