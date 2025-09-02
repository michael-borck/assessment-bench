use anyhow::Result;
use crate::db::models::*;
use crate::llm::{LLMProvider, LLMRequest};

pub mod tiers;
pub mod validation;
pub mod aggregation;

pub use tiers::TierProcessor;
pub use aggregation::ResultAggregator;
pub use validation::ScoreValidator;

pub struct GradingEngine {
    // Future: store configuration, caching, etc.
}

impl GradingEngine {
    pub fn new() -> Self {
        Self {}
    }

    pub async fn grade_submission(
        &self,
        submission: &Submission,
        provider: &dyn LLMProvider,
        tier: GradingTier,
        rubric: &str,
        run_number: u32,
        assignment_spec: Option<&str>,
    ) -> Result<GradingResult> {
        log::info!("Starting grading for submission {} (run {})", submission.id, run_number);
        
        // Prepare the grading prompt based on tier
        let (user_prompt, system_prompt) = TierProcessor::prepare_prompt(
            &tier,
            submission,
            rubric,
            assignment_spec,
        ).await?;

        // Create LLM request
        let llm_request = LLMRequest {
            prompt: user_prompt,
            system_prompt,
            temperature: 0.1, // Low temperature for consistent grading
            max_tokens: Some(2000),
        };

        // Get response from LLM
        let llm_response = provider.generate(llm_request).await?;
        
        // Parse and validate the response
        let parsed_result = self.parse_grading_response(
            &llm_response.content,
            submission,
            &tier,
            run_number,
        ).await?;

        log::info!("Completed grading for submission {} with grade: {:?}", 
                  submission.id, parsed_result.overall_grade);

        Ok(parsed_result)
    }

    async fn parse_grading_response(
        &self,
        response_text: &str,
        submission: &Submission,
        tier: &GradingTier,
        run_number: u32,
    ) -> Result<GradingResult> {
        // Simple parsing logic - in production this would be more sophisticated
        let overall_grade = self.extract_overall_grade(response_text);
        let total_points = self.extract_total_points(response_text);
        let summary_feedback = self.extract_summary_feedback(response_text);
        let strengths = self.extract_strengths(response_text);
        let improvements = self.extract_improvements(response_text);
        
        // Basic validation
        let validation_result = ValidationResult {
            is_valid: overall_grade.is_some() || total_points.is_some(),
            confidence: if overall_grade.is_some() && total_points.is_some() { 0.9 } else { 0.6 },
            issues: vec![],
            extracted_grade: overall_grade.clone(),
            calculated_total: total_points,
        };

        Ok(GradingResult {
            id: uuid::Uuid::new_v4(),
            submission_id: submission.id,
            provider_id: "current_provider".to_string(), // TODO: get actual provider ID
            tier: tier.to_string(),
            run_number,
            created_at: chrono::Utc::now(),
            raw_response: response_text.to_string(),
            overall_grade,
            total_points,
            rubric_scores: vec![], // TODO: implement rubric score extraction
            summary_feedback,
            strengths,
            improvements,
            validation_result,
        })
    }

    fn extract_overall_grade(&self, text: &str) -> Option<String> {
        // Look for patterns like "Grade: A+", "Overall Grade: B", etc.
        use regex::Regex;
        
        if let Ok(re) = Regex::new(r"(?i)(?:overall\s+)?grade:\s*([A-F][+-]?)") {
            if let Some(captures) = re.captures(text) {
                return captures.get(1).map(|m| m.as_str().to_string());
            }
        }
        
        // Look for percentage grades like "85%" or "Score: 85/100"
        if let Ok(re) = Regex::new(r"(?i)(?:score|total):\s*(\d+)(?:/\d+|%)") {
            if let Some(captures) = re.captures(text) {
                if let Some(score_str) = captures.get(1) {
                    if let Ok(score) = score_str.as_str().parse::<u32>() {
                        return Some(self.convert_percentage_to_grade(score));
                    }
                }
            }
        }
        
        None
    }

    fn extract_total_points(&self, text: &str) -> Option<f32> {
        use regex::Regex;
        
        // Look for patterns like "Total: 85/100", "Score: 85", "85 points"
        if let Ok(re) = Regex::new(r"(?i)(?:total|score|points?):\s*(\d+(?:\.\d+)?)(?:/\d+)?") {
            if let Some(captures) = re.captures(text) {
                if let Some(points_str) = captures.get(1) {
                    return points_str.as_str().parse::<f32>().ok();
                }
            }
        }
        
        None
    }

    fn extract_summary_feedback(&self, text: &str) -> Option<String> {
        // Look for sections that contain overall feedback
        let lines: Vec<&str> = text.lines().collect();
        let mut feedback_lines = Vec::new();
        let mut in_feedback_section = false;
        
        for line in lines {
            let lower = line.to_lowercase();
            if lower.contains("summary") || lower.contains("overall") || lower.contains("feedback") {
                in_feedback_section = true;
                continue;
            }
            
            if in_feedback_section {
                if lower.contains("strength") || lower.contains("improvement") || lower.contains("grade") {
                    break;
                }
                if !line.trim().is_empty() {
                    feedback_lines.push(line.trim());
                }
            }
        }
        
        if !feedback_lines.is_empty() {
            Some(feedback_lines.join(" "))
        } else {
            None
        }
    }

    fn extract_strengths(&self, text: &str) -> Vec<String> {
        self.extract_list_section(text, &["strength", "positive", "good"])
    }

    fn extract_improvements(&self, text: &str) -> Vec<String> {
        self.extract_list_section(text, &["improvement", "weakness", "area", "suggestion"])
    }

    fn extract_list_section(&self, text: &str, keywords: &[&str]) -> Vec<String> {
        let lines: Vec<&str> = text.lines().collect();
        let mut items = Vec::new();
        let mut in_section = false;
        
        for line in lines {
            let lower = line.to_lowercase();
            
            // Check if we're entering a relevant section
            if keywords.iter().any(|&keyword| lower.contains(keyword)) {
                in_section = true;
                continue;
            }
            
            // If we're in the section, collect items
            if in_section {
                let trimmed = line.trim();
                
                // Stop if we hit another section
                if lower.contains("grade") || lower.contains("score") || lower.contains("feedback") {
                    break;
                }
                
                // Add non-empty lines that look like list items
                if !trimmed.is_empty() && (trimmed.starts_with('-') || trimmed.starts_with('•') || trimmed.starts_with(&('1'..='9').collect::<String>())) {
                    // Clean up the line
                    let cleaned = trimmed.trim_start_matches(&['-', '•', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ' '][..]);
                    if !cleaned.is_empty() {
                        items.push(cleaned.to_string());
                    }
                }
            }
        }
        
        items
    }

    fn convert_percentage_to_grade(&self, percentage: u32) -> String {
        match percentage {
            97..=100 => "A+".to_string(),
            93..=96 => "A".to_string(),
            90..=92 => "A-".to_string(),
            87..=89 => "B+".to_string(),
            83..=86 => "B".to_string(),
            80..=82 => "B-".to_string(),
            77..=79 => "C+".to_string(),
            73..=76 => "C".to_string(),
            70..=72 => "C-".to_string(),
            67..=69 => "D+".to_string(),
            63..=66 => "D".to_string(),
            60..=62 => "D-".to_string(),
            _ => "F".to_string(),
        }
    }
}

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub enum GradingTier {
    Basic,
    Enhanced,
    AssignmentAware,
}

impl ToString for GradingTier {
    fn to_string(&self) -> String {
        match self {
            GradingTier::Basic => "basic".to_string(),
            GradingTier::Enhanced => "enhanced".to_string(),
            GradingTier::AssignmentAware => "assignment-aware".to_string(),
        }
    }
}