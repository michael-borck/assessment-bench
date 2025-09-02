// Simplified project management commands that work with SimpleDatabase
use crate::db::SimpleDatabase;
use serde::{Deserialize, Serialize};
use tauri::{command, State};

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateProjectRequest {
    pub name: String,
    pub description: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimpleProjectResponse {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
}

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

#[command]
pub async fn create_project_simple(
    request: CreateProjectRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<SimpleProjectResponse>, String> {
    match db.create_project_simple(request.name.clone(), request.description.clone()).await {
        Ok(id) => {
            let response = SimpleProjectResponse {
                id,
                name: request.name,
                description: request.description,
            };
            Ok(ApiResponse::success(response))
        }
        Err(e) => {
            log::error!("Failed to create project: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn list_projects_simple(
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<Vec<SimpleProjectResponse>>, String> {
    match db.list_projects().await {
        Ok(projects) => {
            let responses: Vec<SimpleProjectResponse> = projects
                .into_iter()
                .map(|(id, name)| SimpleProjectResponse {
                    id,
                    name,
                    description: None, // Simplified for now
                })
                .collect();
            Ok(ApiResponse::success(responses))
        }
        Err(e) => {
            log::error!("Failed to list projects: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn delete_project_simple(
    id: String,
    _db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<bool>, String> {
    // For now, return success (actual deletion can be implemented later)
    log::info!("Delete project requested: {}", id);
    Ok(ApiResponse::success(true))
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateProviderRequest {
    pub name: String,
    pub provider_type: String,
    pub model: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimpleProviderResponse {
    pub id: String,
    pub name: String,
    pub provider_type: String,
}

#[command]
pub async fn add_provider_simple(
    request: CreateProviderRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<SimpleProviderResponse>, String> {
    match db.add_provider_simple(
        request.name.clone(),
        request.provider_type.clone(),
        request.model,
    ).await {
        Ok(id) => {
            let response = SimpleProviderResponse {
                id,
                name: request.name,
                provider_type: request.provider_type,
            };
            Ok(ApiResponse::success(response))
        }
        Err(e) => {
            log::error!("Failed to add provider: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[command]
pub async fn list_providers_simple(
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<Vec<SimpleProviderResponse>>, String> {
    match db.list_providers().await {
        Ok(providers) => {
            let responses: Vec<SimpleProviderResponse> = providers
                .into_iter()
                .map(|(id, name, provider_type)| SimpleProviderResponse {
                    id,
                    name,
                    provider_type,
                })
                .collect();
            Ok(ApiResponse::success(responses))
        }
        Err(e) => {
            log::error!("Failed to list providers: {}", e);
            Ok(ApiResponse::error(e.to_string()))
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TestLLMRequest {
    pub provider_id: String,
    pub api_key: String,
    pub prompt: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TestLLMResponse {
    pub success: bool,
    pub response: Option<String>,
    pub tokens_used: Option<u32>,
    pub model: String,
}

#[command]
pub async fn test_llm_provider(
    request: TestLLMRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<TestLLMResponse>, String> {
    use crate::llm::{ProviderFactory, LLMRequest};
    
    // Get provider info from database
    let providers = match db.list_providers().await {
        Ok(providers) => providers,
        Err(e) => {
            log::error!("Failed to get providers: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    };
    
    let provider_info = providers.iter()
        .find(|(id, _, _)| id == &request.provider_id);
    
    let (_id, _name, provider_type) = match provider_info {
        Some(info) => info,
        None => {
            return Ok(ApiResponse::error("Provider not found".to_string()));
        }
    };
    
    // Create provider config JSON
    let config = serde_json::json!({
        "api_key": request.api_key,
        "base_url": if provider_type == "openai" { "https://api.openai.com/v1" } else { "http://localhost:11434" },
        "model": if provider_type == "openai" { "gpt-4o-mini" } else { "llama3.1" },
        "temperature": 0.1,
        "max_tokens": 500
    });
    
    // Create LLM provider
    let provider = match ProviderFactory::create_provider(provider_type, &config.to_string()) {
        Ok(provider) => provider,
        Err(e) => {
            log::error!("Failed to create provider: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    };
    
    // Test the provider
    let llm_request = LLMRequest {
        prompt: request.prompt,
        system_prompt: Some("You are a helpful AI assistant. Keep your response brief and clear.".to_string()),
        temperature: 0.1,
        max_tokens: Some(500),
    };
    
    match provider.generate(llm_request).await {
        Ok(response) => {
            let test_response = TestLLMResponse {
                success: true,
                response: Some(response.content),
                tokens_used: response.tokens_used,
                model: response.model,
            };
            Ok(ApiResponse::success(test_response))
        }
        Err(e) => {
            log::error!("LLM provider test failed: {}", e);
            let test_response = TestLLMResponse {
                success: false,
                response: None,
                tokens_used: None,
                model: "unknown".to_string(),
            };
            Ok(ApiResponse::success(test_response))
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TestGradingRequest {
    pub provider_id: String,
    pub api_key: String,
    pub submission_text: String,
    pub rubric: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TestGradingResponse {
    pub success: bool,
    pub overall_grade: Option<String>,
    pub total_points: Option<f32>,
    pub summary_feedback: Option<String>,
    pub strengths: Vec<String>,
    pub improvements: Vec<String>,
    pub raw_response: String,
}

#[command]
pub async fn test_basic_grading(
    request: TestGradingRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<TestGradingResponse>, String> {
    use crate::llm::ProviderFactory;
    use crate::grading::{GradingEngine, GradingTier};
    use crate::db::models::Submission;
    use chrono::Utc;
    use uuid::Uuid;

    log::info!("Testing basic grading with provider: {}", request.provider_id);
    
    // Get provider info from database
    let providers = match db.list_providers().await {
        Ok(providers) => providers,
        Err(e) => {
            log::error!("Failed to get providers: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    };
    
    let provider_info = providers.iter()
        .find(|(id, _, _)| id == &request.provider_id);
    
    let (_id, _name, provider_type) = match provider_info {
        Some(info) => info,
        None => {
            return Ok(ApiResponse::error("Provider not found".to_string()));
        }
    };
    
    // Create provider config JSON
    let config = serde_json::json!({
        "api_key": request.api_key,
        "base_url": if provider_type == "openai" { "https://api.openai.com/v1" } else { "http://localhost:11434" },
        "model": if provider_type == "openai" { "gpt-4o-mini" } else { "llama3.1" },
        "temperature": 0.1,
        "max_tokens": 2000
    });
    
    // Create LLM provider
    let provider = match ProviderFactory::create_provider(provider_type, &config.to_string()) {
        Ok(provider) => provider,
        Err(e) => {
            log::error!("Failed to create provider: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    };
    
    // Create a mock submission for testing
    let mock_submission = Submission {
        id: Uuid::new_v4(),
        project_id: Uuid::new_v4(),
        original_filename: "test_submission.txt".to_string(),
        file_hash: "test_hash".to_string(),
        file_type: "txt".to_string(),
        word_count: request.submission_text.split_whitespace().count() as u32,
        status: "processed".to_string(),
        extracted_text: Some(request.submission_text.clone()),
        analysis_cache: None,
        imported_at: Utc::now(),
    };
    
    // Create grading engine and perform grading
    let grading_engine = GradingEngine::new();
    
    match grading_engine.grade_submission(
        &mock_submission,
        provider.as_ref(),
        GradingTier::Basic,
        &request.rubric,
        1,
        None, // No assignment spec for basic grading
    ).await {
        Ok(grading_result) => {
            let test_response = TestGradingResponse {
                success: true,
                overall_grade: grading_result.overall_grade,
                total_points: grading_result.total_points,
                summary_feedback: grading_result.summary_feedback,
                strengths: grading_result.strengths,
                improvements: grading_result.improvements,
                raw_response: grading_result.raw_response,
            };
            Ok(ApiResponse::success(test_response))
        }
        Err(e) => {
            log::error!("Grading test failed: {}", e);
            let test_response = TestGradingResponse {
                success: false,
                overall_grade: None,
                total_points: None,
                summary_feedback: None,
                strengths: vec![],
                improvements: vec![],
                raw_response: e.to_string(),
            };
            Ok(ApiResponse::success(test_response))
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MultipleRunsRequest {
    pub provider_id: String,
    pub api_key: String,
    pub submission_text: String,
    pub rubric: String,
    pub num_runs: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MultipleRunsResponse {
    pub success: bool,
    pub run_count: u32,
    pub mean_score: f32,
    pub median_score: f32,
    pub std_deviation: f32,
    pub coefficient_of_variation: f32,
    pub score_range: f32,
    pub reliability_score: f32,
    pub individual_grades: Vec<Option<String>>,
    pub individual_scores: Vec<Option<f32>>,
    pub common_strengths: Vec<String>,
    pub common_improvements: Vec<String>,
    pub individual_responses: Vec<String>,
}

#[command]
pub async fn test_multiple_grading_runs(
    request: MultipleRunsRequest,
    db: State<'_, SimpleDatabase>,
) -> Result<ApiResponse<MultipleRunsResponse>, String> {
    use crate::llm::ProviderFactory;
    use crate::grading::{GradingEngine, GradingTier};
    use crate::grading::aggregation::ResultAggregator;
    use crate::db::models::Submission;
    use chrono::Utc;
    use uuid::Uuid;

    log::info!("Testing multiple grading runs ({}) with provider: {}", request.num_runs, request.provider_id);
    
    // Validate num_runs
    let num_runs = request.num_runs.max(1).min(10); // Limit to reasonable range
    
    // Get provider info from database
    let providers = match db.list_providers().await {
        Ok(providers) => providers,
        Err(e) => {
            log::error!("Failed to get providers: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    };
    
    let provider_info = providers.iter()
        .find(|(id, _, _)| id == &request.provider_id);
    
    let (_id, _name, provider_type) = match provider_info {
        Some(info) => info,
        None => {
            return Ok(ApiResponse::error("Provider not found".to_string()));
        }
    };
    
    // Create provider config JSON
    let config = serde_json::json!({
        "api_key": request.api_key,
        "base_url": if provider_type == "openai" { "https://api.openai.com/v1" } else { "http://localhost:11434" },
        "model": if provider_type == "openai" { "gpt-4o-mini" } else { "llama3.1" },
        "temperature": 0.1,
        "max_tokens": 2000
    });
    
    // Create LLM provider
    let provider = match ProviderFactory::create_provider(provider_type, &config.to_string()) {
        Ok(provider) => provider,
        Err(e) => {
            log::error!("Failed to create provider: {}", e);
            return Ok(ApiResponse::error(e.to_string()));
        }
    };
    
    // Create a mock submission for testing
    let mock_submission = Submission {
        id: Uuid::new_v4(),
        project_id: Uuid::new_v4(),
        original_filename: "test_submission.txt".to_string(),
        file_hash: "test_hash".to_string(),
        file_type: "txt".to_string(),
        word_count: request.submission_text.split_whitespace().count() as u32,
        status: "processed".to_string(),
        extracted_text: Some(request.submission_text.clone()),
        analysis_cache: None,
        imported_at: Utc::now(),
    };
    
    // Create grading engine
    let grading_engine = GradingEngine::new();
    let mut grading_results = Vec::new();
    let mut individual_responses = Vec::new();
    
    // Run multiple grading iterations
    for run_num in 1..=num_runs {
        log::info!("Running grading iteration {}/{}", run_num, num_runs);
        
        match grading_engine.grade_submission(
            &mock_submission,
            provider.as_ref(),
            GradingTier::Basic,
            &request.rubric,
            run_num,
            None,
        ).await {
            Ok(result) => {
                individual_responses.push(result.raw_response.clone());
                grading_results.push(result);
            }
            Err(e) => {
                log::error!("Grading run {} failed: {}", run_num, e);
                // Continue with other runs even if one fails
            }
        }
    }
    
    if grading_results.is_empty() {
        return Ok(ApiResponse::error("All grading runs failed".to_string()));
    }
    
    // Aggregate results
    let aggregated_results = ResultAggregator::aggregate_results(grading_results.clone());
    
    if let Some(aggregated) = aggregated_results.first() {
        let consistency_metrics = ResultAggregator::calculate_consistency_metrics(aggregated);
        
        let individual_grades: Vec<Option<String>> = grading_results.iter()
            .map(|r| r.overall_grade.clone())
            .collect();
            
        let individual_scores: Vec<Option<f32>> = grading_results.iter()
            .map(|r| r.total_points)
            .collect();
        
        let response = MultipleRunsResponse {
            success: true,
            run_count: consistency_metrics.run_count,
            mean_score: aggregated.mean_score,
            median_score: aggregated.median_score,
            std_deviation: aggregated.std_deviation,
            coefficient_of_variation: aggregated.coefficient_of_variation,
            score_range: consistency_metrics.score_range,
            reliability_score: consistency_metrics.reliability_score,
            individual_grades,
            individual_scores,
            common_strengths: aggregated.common_strengths.clone(),
            common_improvements: aggregated.common_improvements.clone(),
            individual_responses,
        };
        
        Ok(ApiResponse::success(response))
    } else {
        Ok(ApiResponse::error("Failed to aggregate results".to_string()))
    }
}