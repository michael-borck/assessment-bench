// Score extraction and validation logic

use crate::db::models::{ValidationResult, ValidationIssue, RubricScore};
use regex::Regex;
use std::collections::HashMap;

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

    /// Enhanced validation with multiple extraction strategies
    pub fn advanced_validate_and_extract(raw_response: &str, expected_rubric: Option<&[String]>) -> ValidationResult {
        let mut issues = Vec::new();
        let mut confidence = 1.0f32;

        // Multiple grade extraction strategies
        let extracted_grade = Self::extract_grade_advanced(raw_response);
        if extracted_grade.is_none() {
            issues.push(ValidationIssue {
                issue_type: "MISSING_GRADE".to_string(),
                severity: "WARNING".to_string(),
                description: "Could not extract overall grade using any method".to_string(),
                suggested_fix: Some("Ensure response contains clear grade indication".to_string()),
            });
            confidence -= 0.15;
        }

        // Enhanced rubric score extraction
        let rubric_scores = Self::extract_rubric_scores_advanced(raw_response, expected_rubric);
        let calculated_total = Self::calculate_total(&rubric_scores);

        // Validate rubric completeness
        if let Some(expected) = expected_rubric {
            let found_criteria: Vec<String> = rubric_scores.iter()
                .map(|s| s.criterion.clone())
                .collect();
            
            for expected_criterion in expected {
                if !found_criteria.iter().any(|c| Self::criteria_match(c, expected_criterion)) {
                    issues.push(ValidationIssue {
                        issue_type: "MISSING_RUBRIC_SCORE".to_string(),
                        severity: "ERROR".to_string(),
                        description: format!("Missing score for criterion: {}", expected_criterion),
                        suggested_fix: Some("Ensure all rubric criteria are scored".to_string()),
                    });
                    confidence -= 0.2;
                }
            }
        }

        // Grade consistency validation
        if let (Some(grade), Some(total)) = (&extracted_grade, calculated_total) {
            let validation_result = Self::validate_grade_consistency(grade, total);
            if !validation_result.is_consistent {
                issues.push(ValidationIssue {
                    issue_type: "GRADE_MISMATCH".to_string(),
                    severity: validation_result.severity,
                    description: validation_result.description,
                    suggested_fix: validation_result.suggested_fix,
                });
                confidence -= validation_result.confidence_penalty;
            }
        }

        // Response quality validation
        let quality_issues = Self::validate_response_quality(raw_response);
        for issue in quality_issues {
            confidence -= 0.1;
            issues.push(issue);
        }

        ValidationResult {
            is_valid: confidence > 0.5,
            confidence: confidence.max(0.0),
            issues,
            extracted_grade,
            calculated_total,
        }
    }

    fn extract_grade_advanced(text: &str) -> Option<String> {
        // Enhanced patterns for grade extraction
        let advanced_patterns = vec![
            // Standard grade patterns
            r"(?i)(?:overall|final|total)\s*(?:grade|score):\s*([A-F][+-]?|\d+(?:\.\d+)?(?:/\d+)?%?)",
            r"(?i)grade:\s*([A-F][+-]?|\d+(?:\.\d+)?(?:/\d+)?%?)",
            r"(?i)(?:score|points):\s*(\d+(?:\.\d+)?)\s*(?:out\s*of|/)\s*(\d+)",
            r"(?i)(?:received|earned|scored):\s*(\d+(?:\.\d+)?)\s*(?:points?|pts?)",
            
            // Natural language patterns
            r"(?i)(?:receives?|gets?|earns?|scores?)\s*(?:a|an)?\s*([A-F][+-]?)",
            r"(?i)(?:rating|performance):\s*([A-F][+-]?)",
            r"(?i)(\d+(?:\.\d+)?)(?:%|\s*percent|\s*out\s*of\s*100)",
            
            // Fraction patterns
            r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)",
            
            // End-of-response patterns
            r"(?i)(?:final|overall|total).*?([A-F][+-]?|\d+(?:\.\d+)?%?)$",
        ];

        for pattern in advanced_patterns {
            if let Ok(regex) = Regex::new(pattern) {
                if let Some(captures) = regex.captures(text) {
                    if let Some(grade) = captures.get(1) {
                        let grade_str = grade.as_str().trim();
                        if !grade_str.is_empty() {
                            // Handle fraction formats
                            if let Some(denominator) = captures.get(2) {
                                let num: f32 = grade_str.parse().unwrap_or(0.0);
                                let den: f32 = denominator.as_str().parse().unwrap_or(1.0);
                                let percentage = (num / den * 100.0).round();
                                return Some(format!("{}", percentage));
                            }
                            return Some(grade_str.to_string());
                        }
                    }
                }
            }
        }

        // Fallback: look for any grade-like patterns at end of response
        Self::extract_grade(text)
    }

    fn extract_rubric_scores_advanced(
        text: &str,
        expected_criteria: Option<&[String]>
    ) -> Vec<RubricScore> {
        let mut scores = Vec::new();
        let mut found_criteria = HashMap::new();
        
        // Enhanced patterns for rubric score extraction
        let score_patterns = vec![
            // Standard format: "Criterion: X/Y points"
            r"(?i)([^:\n]{5,40}):\s*(\d+(?:\.\d+)?)\s*(?:/\s*|\s+out\s+of\s+)(\d+(?:\.\d+)?)\s*(?:points?|pts?)?",
            
            // Format: "Criterion: X points"
            r"(?i)([^:\n]{5,40}):\s*(\d+(?:\.\d+)?)\s*(?:points?|pts?)",
            
            // Format: "Criterion (X/Y)"
            r"(?i)([^(\n]{5,40})\s*\(\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*\)",
            
            // Format: "Score for Criterion: X"
            r"(?i)(?:score\s+for\s+|points?\s+for\s+)?([^:\n]{5,40}):\s*(\d+(?:\.\d+)?)",
            
            // Table-like format
            r"(?i)([A-Z][^|\n]{4,30})\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*(\d+(?:\.\d+)?)",
        ];

        for pattern in score_patterns {
            if let Ok(regex) = Regex::new(pattern) {
                for captures in regex.captures_iter(text) {
                    if let (Some(criterion_match), Some(points_match)) = (captures.get(1), captures.get(2)) {
                        let criterion = Self::normalize_criterion_name(criterion_match.as_str());
                        let points_awarded: f32 = points_match.as_str().parse().unwrap_or(0.0);
                        
                        // Get points possible from third capture group or default
                        let points_possible = captures.get(3)
                            .and_then(|m| m.as_str().parse().ok())
                            .unwrap_or_else(|| {
                                // Try to infer from expected criteria or use awarded points
                                Self::infer_points_possible(&criterion, expected_criteria, points_awarded)
                            });

                        // Avoid duplicates
                        if !found_criteria.contains_key(&criterion) {
                            found_criteria.insert(criterion.clone(), true);
                            scores.push(RubricScore {
                                criterion,
                                points_awarded,
                                points_possible,
                                comments: Self::extract_criterion_comments(text, criterion_match.as_str()),
                            });
                        }
                    }
                }
            }
        }

        // If no scores found with patterns, try line-by-line analysis
        if scores.is_empty() {
            scores = Self::extract_scores_line_by_line(text, expected_criteria);
        }

        scores
    }

    fn normalize_criterion_name(raw: &str) -> String {
        raw.trim()
            .replace(|c: char| !c.is_alphanumeric() && c != ' ', "")
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ")
            .to_lowercase()
    }

    fn criteria_match(found: &str, expected: &str) -> bool {
        let found_norm = Self::normalize_criterion_name(found);
        let expected_norm = Self::normalize_criterion_name(expected);
        
        // Exact match
        if found_norm == expected_norm {
            return true;
        }
        
        // Partial match (70% of words in common)
        let found_words: Vec<&str> = found_norm.split_whitespace().collect();
        let expected_words: Vec<&str> = expected_norm.split_whitespace().collect();
        
        let common_words = found_words.iter()
            .filter(|word| expected_words.contains(word))
            .count();
        
        let total_words = expected_words.len().max(1);
        (common_words as f32 / total_words as f32) >= 0.7
    }

    fn infer_points_possible(
        _criterion: &str,
        expected_criteria: Option<&[String]>,
        points_awarded: f32
    ) -> f32 {
        // Simple heuristics for inferring maximum points
        if points_awarded <= 5.0 { return 5.0; }
        if points_awarded <= 10.0 { return 10.0; }
        if points_awarded <= 20.0 { return 20.0; }
        if points_awarded <= 25.0 { return 25.0; }
        if points_awarded <= 50.0 { return 50.0; }
        if points_awarded <= 100.0 { return 100.0; }
        
        // If we have expected criteria, assume even distribution
        if let Some(criteria) = expected_criteria {
            return 100.0 / criteria.len() as f32;
        }
        
        points_awarded
    }

    fn extract_criterion_comments(text: &str, criterion: &str) -> Option<String> {
        // Look for comments following the criterion
        let pattern = format!(r"(?i){}[:\s]*[^\n]*\n\s*([^:\n]{{10,}})", regex::escape(criterion));
        
        if let Ok(regex) = Regex::new(&pattern) {
            if let Some(captures) = regex.captures(text) {
                if let Some(comment) = captures.get(1) {
                    let comment_text = comment.as_str().trim();
                    if comment_text.len() > 5 && !comment_text.parse::<f32>().is_ok() {
                        return Some(comment_text.to_string());
                    }
                }
            }
        }
        
        None
    }

    fn extract_scores_line_by_line(
        text: &str,
        expected_criteria: Option<&[String]>
    ) -> Vec<RubricScore> {
        let mut scores = Vec::new();
        let lines: Vec<&str> = text.lines().collect();
        
        for line in lines {
            let line = line.trim();
            if line.is_empty() { continue; }
            
            // Look for number patterns in each line
            if let Ok(regex) = Regex::new(r"(\d+(?:\.\d+)?)") {
                if let Some(number_match) = regex.find(line) {
                    let number: f32 = number_match.as_str().parse().unwrap_or(0.0);
                    
                    // Extract potential criterion name (text before the number)
                    let criterion_part = &line[..number_match.start()].trim();
                    
                    if criterion_part.len() > 3 && number > 0.0 {
                        let criterion = Self::normalize_criterion_name(criterion_part);
                        
                        scores.push(RubricScore {
                            criterion: criterion.clone(),
                            points_awarded: number,
                            points_possible: Self::infer_points_possible(&criterion, expected_criteria, number),
                            comments: None,
                        });
                    }
                }
            }
        }
        
        scores
    }

    fn validate_grade_consistency(grade: &str, total: f32) -> GradeConsistencyResult {
        if let Some(grade_numeric) = Self::grade_to_numeric(grade) {
            let diff = (grade_numeric - total).abs();
            
            if diff <= 2.0 {
                return GradeConsistencyResult {
                    is_consistent: true,
                    severity: "INFO".to_string(),
                    description: "Grade and total are consistent".to_string(),
                    suggested_fix: None,
                    confidence_penalty: 0.0,
                };
            } else if diff <= 5.0 {
                return GradeConsistencyResult {
                    is_consistent: false,
                    severity: "WARNING".to_string(),
                    description: format!("Minor inconsistency: grade {} vs total {}", grade_numeric, total),
                    suggested_fix: Some("Verify calculation accuracy".to_string()),
                    confidence_penalty: 0.1,
                };
            } else {
                return GradeConsistencyResult {
                    is_consistent: false,
                    severity: "ERROR".to_string(),
                    description: format!("Major inconsistency: grade {} vs total {}", grade_numeric, total),
                    suggested_fix: Some("Recalculate or use total from rubric scores".to_string()),
                    confidence_penalty: 0.3,
                };
            }
        }
        
        GradeConsistencyResult {
            is_consistent: false,
            severity: "WARNING".to_string(),
            description: "Could not validate grade consistency".to_string(),
            suggested_fix: Some("Ensure grade is in recognizable format".to_string()),
            confidence_penalty: 0.1,
        }
    }

    fn validate_response_quality(text: &str) -> Vec<ValidationIssue> {
        let mut issues = Vec::new();
        
        // Check response length
        if text.len() < 100 {
            issues.push(ValidationIssue {
                issue_type: "RESPONSE_TOO_SHORT".to_string(),
                severity: "WARNING".to_string(),
                description: "Response appears too short for comprehensive grading".to_string(),
                suggested_fix: Some("Increase max_tokens or ask for more detailed response".to_string()),
            });
        }
        
        // Check for common AI disclaimers or refusals
        let refusal_patterns = vec![
            r"(?i)I cannot",
            r"(?i)I'm unable to",
            r"(?i)as an AI",
            r"(?i)I don't have access",
            r"(?i)insufficient information",
        ];
        
        for pattern in refusal_patterns {
            if let Ok(regex) = Regex::new(pattern) {
                if regex.is_match(text) {
                    issues.push(ValidationIssue {
                        issue_type: "AI_REFUSAL".to_string(),
                        severity: "ERROR".to_string(),
                        description: "AI model refused to provide grading".to_string(),
                        suggested_fix: Some("Adjust prompt to be more specific and clear".to_string()),
                    });
                    break;
                }
            }
        }
        
        // Check for structured feedback
        let feedback_indicators = vec!["strengths", "weaknesses", "improvements", "feedback"];
        let has_feedback = feedback_indicators.iter().any(|indicator| {
            text.to_lowercase().contains(indicator)
        });
        
        if !has_feedback {
            issues.push(ValidationIssue {
                issue_type: "MISSING_FEEDBACK".to_string(),
                severity: "WARNING".to_string(),
                description: "Response lacks structured feedback sections".to_string(),
                suggested_fix: Some("Request explicit strengths and improvement areas".to_string()),
            });
        }
        
        issues
    }
}

#[derive(Debug)]
struct GradeConsistencyResult {
    is_consistent: bool,
    severity: String,
    description: String,
    suggested_fix: Option<String>,
    confidence_penalty: f32,
}