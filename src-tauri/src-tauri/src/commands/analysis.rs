use super::ApiResponse;
use crate::db::Database;
use crate::document_analysis::{DocumentLensClient, models::AnalysisRequest, DocumentAnalysis};
use serde::{Deserialize, Serialize};
use tauri::{command, State};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub struct AggregatedResultResponse {
    pub submission_id: String,
    pub provider_id: String,
    pub tier: String,
    pub mean_score: f32,
    pub median_score: f32,
    pub std_deviation: f32,
    pub coefficient_of_variation: f32,
    pub run_count: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ExportResultsRequest {
    pub project_id: String,
    pub format: String, // 'csv', 'json', 'pdf'
    pub include_raw_responses: bool,
}

#[command]
pub async fn get_aggregated_results(
    project_id: String,
    _db: State<'_, Database>,
) -> Result<ApiResponse<Vec<AggregatedResultResponse>>, String> {
    let _project_id = match Uuid::parse_str(&project_id) {
        Ok(id) => id,
        Err(_) => return Ok(ApiResponse::error("Invalid project ID format".to_string())),
    };

    // TODO: Implement aggregation logic
    let results = vec![];
    Ok(ApiResponse::success(results))
}

#[command]
pub async fn export_results(
    request: ExportResultsRequest,
    _db: State<'_, Database>,
) -> Result<ApiResponse<String>, String> {
    let _project_id = match Uuid::parse_str(&request.project_id) {
        Ok(id) => id,
        Err(_) => return Ok(ApiResponse::error("Invalid project ID format".to_string())),
    };

    // TODO: Implement export functionality
    let export_path = format!("export_{}.{}", request.project_id, request.format);
    Ok(ApiResponse::success(export_path))
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DocumentLensAnalysisRequest {
    pub text: String,
    pub analysis_type: String, // 'academic', 'comprehensive', 'writing_quality', 'readability'
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DocumentLensAnalysisResponse {
    pub analysis: DocumentAnalysis,
    pub processing_time_ms: u64,
}

#[command]
pub async fn analyze_document_with_lens(
    request: DocumentLensAnalysisRequest,
) -> Result<ApiResponse<DocumentLensAnalysisResponse>, String> {
    let start_time = std::time::Instant::now();
    
    // Initialize DocumentLens client
    let client = match DocumentLensClient::new(None) {
        Ok(client) => client,
        Err(e) => return Ok(ApiResponse::error(format!("Failed to initialize DocumentLens client: {}", e))),
    };
    
    // Create analysis request based on type
    let analysis_request = match request.analysis_type.as_str() {
        "academic" => AnalysisRequest::new_academic(request.text),
        "comprehensive" => AnalysisRequest::new_comprehensive(request.text),
        _ => AnalysisRequest::new_academic(request.text), // Default to academic
    };
    
    // Perform analysis
    let analysis = match client.analyze_document(analysis_request).await {
        Ok(analysis) => analysis,
        Err(e) => return Ok(ApiResponse::error(format!("Document analysis failed: {}", e))),
    };
    
    let processing_time_ms = start_time.elapsed().as_millis() as u64;
    
    let response = DocumentLensAnalysisResponse {
        analysis,
        processing_time_ms,
    };
    
    Ok(ApiResponse::success(response))
}

#[command]
pub async fn test_documentlens_integration() -> Result<ApiResponse<String>, String> {
    let sample_text = r#"
    The development of artificial intelligence has revolutionized numerous aspects of modern society. This technological advancement has profound implications for education, healthcare, and business sectors. Machine learning algorithms, a subset of AI, enable computers to learn and adapt without explicit programming.

    In educational contexts, AI-powered systems can personalize learning experiences for individual students. These systems analyze student performance data to identify learning gaps and suggest targeted interventions. Furthermore, automated grading systems can provide immediate feedback on assignments, allowing educators to focus on higher-level instructional activities.

    The healthcare industry has similarly benefited from AI integration. Diagnostic imaging systems powered by deep learning can detect anomalies with remarkable accuracy, often exceeding human performance in specific tasks. Predictive analytics help healthcare providers identify at-risk patients and implement preventive measures.

    However, the widespread adoption of AI also raises important ethical considerations. Issues of privacy, algorithmic bias, and job displacement require careful examination. As society continues to integrate AI technologies, establishing robust ethical frameworks becomes increasingly critical.

    In conclusion, while artificial intelligence offers tremendous potential for societal advancement, thoughtful implementation and ongoing evaluation are essential to maximize benefits while mitigating risks.
    "#;
    
    let client = match DocumentLensClient::new(None) {
        Ok(client) => client,
        Err(e) => return Ok(ApiResponse::error(format!("Failed to initialize client: {}", e))),
    };
    
    let request = AnalysisRequest::new_academic(sample_text.to_string());
    
    match client.analyze_document(request).await {
        Ok(analysis) => {
            let summary = format!(
                "DocumentLens Analysis Test Results:\n\n{}\n\nOverall Quality Score: {:.1}/10",
                analysis.to_formatted_string(),
                analysis.overall_score()
            );
            Ok(ApiResponse::success(summary))
        },
        Err(e) => Ok(ApiResponse::error(format!("Analysis failed: {}", e))),
    }
}