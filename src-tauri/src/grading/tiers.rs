// Grading tier implementations

use super::GradingTier;
use crate::db::models::{Submission, DocumentAnalysis};
use anyhow::Result;

pub struct TierProcessor;

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
        // TODO: Integrate with DocumentLens API to get analysis
        let analysis_text = if let Some(_analysis) = &submission.analysis_cache {
            // Format analysis data into text
            "Text analysis: Word count: {}, Reading level: {}, etc.".to_string()
        } else {
            "No analysis data available".to_string()
        };

        let system_prompt = Some(
            "You are an expert academic grader with access to detailed text analysis. Use both the content and the analytical metrics to provide comprehensive grading.".to_string()
        );

        let user_prompt = format!(
            r#"Please grade the following submission using the provided rubric and text analysis:

RUBRIC:
{}

TEXT ANALYSIS:
{}

SUBMISSION:
{}

Use the text analysis to inform your grading, particularly for writing quality, readability, and technical aspects. Provide detailed feedback that incorporates both content assessment and writing quality metrics."#,
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
}