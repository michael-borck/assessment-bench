// Statistical aggregation of multiple grading runs

use crate::db::models::{GradingResult, AggregatedResult};
use std::collections::HashMap;

#[allow(dead_code)]
pub struct ResultAggregator;

#[allow(dead_code)]
impl ResultAggregator {
    pub fn aggregate_results(results: Vec<GradingResult>) -> Vec<AggregatedResult> {
        // Group results by submission_id, provider_id, and tier
        let mut grouped_results: HashMap<(String, String, String), Vec<GradingResult>> = HashMap::new();

        for result in results {
            let key = (
                result.submission_id.to_string(),
                result.provider_id.clone(),
                result.tier.clone(),
            );
            grouped_results.entry(key).or_insert_with(Vec::new).push(result);
        }

        let mut aggregated_results = Vec::new();

        for ((submission_id, provider_id, tier), group_results) in grouped_results {
            if group_results.is_empty() {
                continue;
            }

            let scores: Vec<f32> = group_results
                .iter()
                .filter_map(|r| r.total_points)
                .collect();

            if scores.is_empty() {
                continue;
            }

            let mean_score = Self::calculate_mean(&scores);
            let median_score = Self::calculate_median(&scores);
            let std_deviation = Self::calculate_std_deviation(&scores, mean_score);
            let coefficient_of_variation = if mean_score != 0.0 {
                std_deviation / mean_score
            } else {
                0.0
            };

            // Aggregate feedback
            let all_strengths: Vec<String> = group_results
                .iter()
                .flat_map(|r| r.strengths.iter().cloned())
                .collect();
            
            let all_improvements: Vec<String> = group_results
                .iter()
                .flat_map(|r| r.improvements.iter().cloned())
                .collect();

            let common_strengths = Self::find_common_items(&all_strengths);
            let common_improvements = Self::find_common_items(&all_improvements);

            aggregated_results.push(AggregatedResult {
                submission_id: uuid::Uuid::parse_str(&submission_id).unwrap(),
                provider_id,
                tier,
                mean_score,
                median_score,
                std_deviation,
                coefficient_of_variation,
                individual_results: group_results,
                consensus_feedback: None, // TODO: Implement consensus feedback generation
                common_strengths,
                common_improvements,
            });
        }

        aggregated_results
    }

    fn calculate_mean(values: &[f32]) -> f32 {
        if values.is_empty() {
            return 0.0;
        }
        values.iter().sum::<f32>() / values.len() as f32
    }

    fn calculate_median(values: &[f32]) -> f32 {
        if values.is_empty() {
            return 0.0;
        }

        let mut sorted_values = values.to_vec();
        sorted_values.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let len = sorted_values.len();
        if len % 2 == 0 {
            (sorted_values[len / 2 - 1] + sorted_values[len / 2]) / 2.0
        } else {
            sorted_values[len / 2]
        }
    }

    fn calculate_std_deviation(values: &[f32], mean: f32) -> f32 {
        if values.len() <= 1 {
            return 0.0;
        }

        let variance = values
            .iter()
            .map(|value| {
                let diff = value - mean;
                diff * diff
            })
            .sum::<f32>() / (values.len() - 1) as f32;

        variance.sqrt()
    }

    fn find_common_items(items: &[String]) -> Vec<String> {
        let mut item_counts: HashMap<String, usize> = HashMap::new();
        
        for item in items {
            let normalized = item.to_lowercase().trim().to_string();
            *item_counts.entry(normalized).or_insert(0) += 1;
        }

        // Return items that appear more than once (common across multiple runs)
        item_counts
            .into_iter()
            .filter(|(_, count)| *count > 1)
            .map(|(item, _)| item)
            .collect()
    }

    pub fn calculate_consistency_metrics(aggregated: &AggregatedResult) -> ConsistencyMetrics {
        let scores: Vec<f32> = aggregated
            .individual_results
            .iter()
            .filter_map(|r| r.total_points)
            .collect();

        ConsistencyMetrics {
            run_count: scores.len() as u32,
            score_range: if scores.len() > 1 {
                scores.iter().max_by(|a, b| a.partial_cmp(b).unwrap()).unwrap() -
                scores.iter().min_by(|a, b| a.partial_cmp(b).unwrap()).unwrap()
            } else {
                0.0
            },
            reliability_score: Self::calculate_reliability(&scores),
        }
    }

    fn calculate_reliability(scores: &[f32]) -> f32 {
        if scores.len() < 2 {
            return 1.0; // Perfect reliability with single score
        }

        let mean = Self::calculate_mean(scores);
        let std_dev = Self::calculate_std_deviation(scores, mean);
        
        // Reliability based on coefficient of variation (lower is more reliable)
        let cv = if mean != 0.0 { std_dev / mean } else { 0.0 };
        
        // Convert to 0-1 scale where 1 is most reliable
        (1.0 - cv.min(1.0)).max(0.0)
    }
}

#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct ConsistencyMetrics {
    pub run_count: u32,
    pub score_range: f32,
    pub reliability_score: f32,
}