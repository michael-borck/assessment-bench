// Score extraction and validation logic

use crate::db::models::{ValidationResult, ValidationIssue, RubricScore};
// anyhow::Result not used in current implementation
use regex::Regex;

#[allow(dead_code)]
pub struct ScoreValidator;

#[allow(dead_code)]
impl ScoreValidator {
    pub fn validate_and_extract(raw_response: &str) -> ValidationResult {
        let mut issues = Vec::new();
        let mut confidence = 1.0f32;

        // Try to extract overall grade
        let extracted_grade = Self::extract_grade(raw_response);
        if extracted_grade.is_none() {
            issues.push(ValidationIssue {
                issue_type: "MISSING_GRADE".to_string(),
                severity: "WARNING".to_string(),
                description: "Could not extract overall grade from response".to_string(),
                suggested_fix: Some("Look for grade patterns like A+, 85/100, etc.".to_string()),
            });
            confidence -= 0.2;
        }

        // Try to extract rubric scores
        let rubric_scores = Self::extract_rubric_scores(raw_response);
        let calculated_total = Self::calculate_total(&rubric_scores);

        // Validate consistency between extracted grade and calculated total
        if let (Some(grade), Some(total)) = (&extracted_grade, calculated_total) {
            let grade_numeric = Self::grade_to_numeric(grade);
            if let Some(grade_num) = grade_numeric {
                let diff = (grade_num - total).abs();
                if diff > 5.0 {
                    issues.push(ValidationIssue {
                        issue_type: "GRADE_MISMATCH".to_string(),
                        severity: "ERROR".to_string(),
                        description: format!(
                            "Grade mismatch: extracted {} ({}) vs calculated {}", 
                            grade, grade_num, total
                        ),
                        suggested_fix: Some("Use calculated total from rubric scores".to_string()),
                    });
                    confidence -= 0.3;
                }
            }
        }

        ValidationResult {
            is_valid: confidence > 0.5,
            confidence,
            issues,
            extracted_grade,
            calculated_total,
        }
    }

    fn extract_grade(text: &str) -> Option<String> {
        // Try different grade patterns
        let patterns = vec![
            r"(?i)(?:overall grade|final grade|grade):\s*([A-F][+-]?)",
            r"(?i)(?:score|points):\s*(\d+(?:\.\d+)?)\s*(?:/\s*(\d+))?",
            r"([A-F][+-]?)\s*(?:grade|final)",
            r"(\d+(?:\.\d+)?)/(\d+)",
            r"(\d+(?:\.\d+)?)%",
        ];

        for pattern in patterns {
            if let Ok(regex) = Regex::new(pattern) {
                if let Some(captures) = regex.captures(text) {
                    if let Some(grade) = captures.get(1) {
                        return Some(grade.as_str().to_string());
                    }
                }
            }
        }

        None
    }

    fn extract_rubric_scores(text: &str) -> Vec<RubricScore> {
        let mut scores = Vec::new();
        
        // Look for criterion patterns
        let criterion_pattern = r"(?i)([^:\n]+):\s*(\d+(?:\.\d+)?)\s*(?:/\s*(\d+))?";
        
        if let Ok(regex) = Regex::new(criterion_pattern) {
            for captures in regex.captures_iter(text) {
                if let (Some(criterion), Some(points)) = (captures.get(1), captures.get(2)) {
                    let points_awarded = points.as_str().parse().unwrap_or(0.0);
                    let points_possible = captures.get(3)
                        .and_then(|m| m.as_str().parse().ok())
                        .unwrap_or(points_awarded);

                    scores.push(RubricScore {
                        criterion: criterion.as_str().trim().to_string(),
                        points_awarded,
                        points_possible,
                        comments: None,
                    });
                }
            }
        }

        scores
    }

    fn calculate_total(rubric_scores: &[RubricScore]) -> Option<f32> {
        if rubric_scores.is_empty() {
            return None;
        }

        let total = rubric_scores.iter().map(|s| s.points_awarded).sum();
        Some(total)
    }

    fn grade_to_numeric(grade: &str) -> Option<f32> {
        match grade.to_uppercase().as_str() {
            "A+" => Some(97.0),
            "A" => Some(93.0),
            "A-" => Some(90.0),
            "B+" => Some(87.0),
            "B" => Some(83.0),
            "B-" => Some(80.0),
            "C+" => Some(77.0),
            "C" => Some(73.0),
            "C-" => Some(70.0),
            "D+" => Some(67.0),
            "D" => Some(63.0),
            "D-" => Some(60.0),
            "F" => Some(50.0),
            _ => {
                // Try to parse as numeric
                if let Ok(num) = grade.parse::<f32>() {
                    Some(num)
                } else if grade.contains('/') {
                    // Handle fraction format like "85/100"
                    let parts: Vec<&str> = grade.split('/').collect();
                    if parts.len() == 2 {
                        if let (Ok(numerator), Ok(denominator)) = (
                            parts[0].parse::<f32>(),
                            parts[1].parse::<f32>()
                        ) {
                            return Some((numerator / denominator) * 100.0);
                        }
                    }
                    None
                } else if grade.ends_with('%') {
                    grade.trim_end_matches('%').parse().ok()
                } else {
                    None
                }
            }
        }
    }
}