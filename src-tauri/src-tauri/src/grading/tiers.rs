// Grading tier implementations

use super::GradingTier;
use crate::db::models::Submission;
use anyhow::Result;

#[allow(dead_code)]
pub struct TierProcessor;

#[allow(dead_code)]
impl TierProcessor {
    pub async fn prepare_prompt(
        tier: &GradingTier,
        submission: &Submission,
        rubric: &str,
        assignment_spec: Option<&str>,
    ) -> Result<(String, Option<String>)> {
        match tier {
            GradingTier::Basic => Self::basic_prompt(submission, rubric).await,
            GradingTier::Enhanced => Self::enhanced_prompt(submission, rubric).await,
            GradingTier::AssignmentAware => {
                Self::assignment_aware_prompt(submission, rubric, assignment_spec).await
            }
        }
    }

    async fn basic_prompt(
        submission: &Submission,
        rubric: &str,
    ) -> Result<(String, Option<String>)> {
        let system_prompt = Some(
            "You are an expert academic grader. Provide detailed, constructive feedback and accurate scoring based on the provided rubric.".to_string()
        );

        let user_prompt = format!(
            r#"Please grade the following submission using the provided rubric:

RUBRIC:
{}

SUBMISSION:
{}

Please provide:
1. Overall grade
2. Score for each rubric criterion
3. Detailed feedback explaining your reasoning
4. Strengths of the submission
5. Areas for improvement

Format your response clearly with sections for each component."#,
            rubric,
            submission.extracted_text.as_ref().unwrap_or(&"No text extracted".to_string())
        );

        Ok((user_prompt, system_prompt))
    }

    async fn enhanced_prompt(
        submission: &Submission,
        rubric: &str,
    ) -> Result<(String, Option<String>)> {
        // Get or create DocumentLens analysis
        let analysis_text = if let Some(cached_analysis) = &submission.analysis_cache {
            if let Some(documentlens_data) = &cached_analysis.documentlens_analysis {
                documentlens_data.to_formatted_string()
            } else {
                // Perform DocumentLens analysis if not cached
                match Self::analyze_document_with_lens(&submission.extracted_text).await {
                    Ok(analysis) => analysis.to_formatted_string(),
                    Err(e) => {
                        log::warn!("Failed to perform DocumentLens analysis: {}", e);
                        Self::fallback_analysis_text(submission)
                    }
                }
            }
        } else {
            // Perform DocumentLens analysis
            match Self::analyze_document_with_lens(&submission.extracted_text).await {
                Ok(analysis) => analysis.to_formatted_string(),
                Err(e) => {
                    log::warn!("Failed to perform DocumentLens analysis: {}", e);
                    Self::fallback_analysis_text(submission)
                }
            }
        };

        let system_prompt = Some(
            "You are an expert academic grader with access to detailed text analysis from DocumentLens. Use both the content and the comprehensive analytical metrics to provide thorough, evidence-based grading. Pay special attention to writing quality, readability, structure, and academic rigor as indicated by the analysis.".to_string()
        );

        let user_prompt = format!(
            r#"Please grade the following submission using the provided rubric and comprehensive text analysis:

RUBRIC:
{}

DETAILED TEXT ANALYSIS:
{}

SUBMISSION:
{}

GRADING INSTRUCTIONS:
Use the detailed text analysis to inform your grading across multiple dimensions:

1. CONTENT QUALITY: Use the depth of analysis, critical thinking, and argument strength metrics
2. WRITING QUALITY: Consider clarity, coherence, grammar, and vocabulary diversity scores
3. STRUCTURE: Evaluate based on paragraph coherence, logical flow, and structural analysis
4. ACADEMIC RIGOR: Incorporate reading level, academic vocabulary usage, and evidence usage
5. TECHNICAL ASPECTS: Consider sentence variety, linguistic features, and complexity

Provide specific feedback that references the analytical metrics where relevant, and explain how the quantitative analysis supports your qualitative assessment."#,
            rubric,
            analysis_text,
            submission.extracted_text.as_ref().unwrap_or(&"No text extracted".to_string())
        );

        Ok((user_prompt, system_prompt))
    }

    async fn assignment_aware_prompt(
        submission: &Submission,
        rubric: &str,
        assignment_spec: Option<&str>,
    ) -> Result<(String, Option<String>)> {
        let assignment_context = assignment_spec.unwrap_or("No assignment specification provided");

        let system_prompt = Some(
            "You are an expert academic grader with full context of the assignment requirements. Evaluate how well the submission meets the specific learning objectives and assignment criteria.".to_string()
        );

        let user_prompt = format!(
            r#"Please grade the following submission using the complete assignment context:

ASSIGNMENT SPECIFICATION:
{}

RUBRIC:
{}

SUBMISSION:
{}

Evaluate the submission against:
1. Assignment-specific requirements and learning objectives
2. How well it addresses the prompt/question
3. Rubric criteria with assignment context
4. Overall alignment with course goals

Provide detailed feedback that shows how the submission performs against the specific assignment requirements."#,
            assignment_context,
            rubric,
            submission.extracted_text.as_ref().unwrap_or(&"No text extracted".to_string())
        );

        Ok((user_prompt, system_prompt))
    }

    async fn analyze_document_with_lens(
        text: &Option<String>,
    ) -> Result<crate::document_analysis::DocumentAnalysis> {
        use crate::document_analysis::{DocumentLensClient, models::AnalysisRequest};
        
        let text_content = text.as_ref().ok_or_else(|| anyhow::anyhow!("No text to analyze"))?;
        
        // Initialize DocumentLens client (API key would come from config)
        let client = DocumentLensClient::new(None)?; // Use None for mock implementation
        
        let request = AnalysisRequest::new_academic(text_content.clone());
        client.analyze_document(request).await
    }

    fn fallback_analysis_text(submission: &Submission) -> String {
        let word_count = submission.word_count;
        let default_text = "".to_string();
        let text = submission.extracted_text.as_ref().unwrap_or(&default_text);
        let sentence_count = text.matches(&['.', '!', '?'][..]).count();
        let paragraph_count = text.split("\n\n").filter(|p| !p.trim().is_empty()).count();
        
        format!(
            r#"BASIC TEXT ANALYSIS (DocumentLens unavailable):

Basic Metrics:
- Word Count: {}
- Estimated Sentence Count: {}  
- Estimated Paragraph Count: {}
- Average Sentence Length: {:.1} words

Note: Advanced writing quality metrics, readability scores, and structural analysis are unavailable. Grading will rely primarily on content assessment."#,
            word_count,
            sentence_count,
            paragraph_count,
            if sentence_count > 0 { word_count as f32 / sentence_count as f32 } else { 0.0 }
        )
    }
}