use super::models::*;
use super::DocumentAnalysis;
use anyhow::Result;
use reqwest::{Client, header::HeaderMap};
use std::time::Duration;
use tokio::time::sleep;

pub struct DocumentLensClient {
    client: Client,
    base_url: String,
    api_key: Option<String>,
}

impl DocumentLensClient {
    pub fn new(api_key: Option<String>) -> Result<Self> {
        let mut headers = HeaderMap::new();
        
        if let Some(key) = &api_key {
            headers.insert("Authorization", format!("Bearer {}", key).parse()?);
        }
        headers.insert("Content-Type", "application/json".parse()?);

        let client = Client::builder()
            .default_headers(headers)
            .timeout(Duration::from_secs(30))
            .build()?;

        Ok(Self {
            client,
            base_url: "https://api.documentlens.io/v1".to_string(), // Hypothetical API
            api_key,
        })
    }

    pub async fn analyze_document(&self, request: AnalysisRequest) -> Result<DocumentAnalysis> {
        // For now, we'll implement a mock analysis since DocumentLens is hypothetical
        // In a real implementation, this would make HTTP requests to the actual API
        self.mock_analysis(&request.text).await
    }

    async fn mock_analysis(&self, text: &str) -> Result<DocumentAnalysis> {
        // Simulate API processing time
        sleep(Duration::from_millis(500)).await;

        // Perform basic text analysis
        let word_count = text.split_whitespace().count() as u32;
        let sentence_count = text.matches(&['.', '!', '?'][..]).count() as u32;
        let paragraph_count = text.split("\n\n").filter(|p| !p.trim().is_empty()).count() as u32;
        
        // Calculate basic metrics
        let avg_sentence_length = if sentence_count > 0 { 
            word_count as f32 / sentence_count as f32 
        } else { 
            0.0 
        };

        // Mock sophisticated analysis based on text characteristics
        let complexity_score = Self::calculate_complexity(text, avg_sentence_length);
        let quality_scores = Self::calculate_quality_scores(text, word_count);
        let structure_scores = Self::analyze_structure(text);
        let content_scores = Self::analyze_content(text, word_count);

        Ok(DocumentAnalysis {
            word_count,
            sentence_count,
            paragraph_count,
            reading_level: Self::calculate_reading_level(text, avg_sentence_length, complexity_score),
            writing_quality: quality_scores,
            linguistic_features: Self::analyze_linguistic_features(text, avg_sentence_length),
            structure_analysis: structure_scores,
            content_metrics: content_scores,
        })
    }

    fn calculate_complexity(text: &str, avg_sentence_length: f32) -> f32 {
        let long_words = text.split_whitespace()
            .filter(|word| word.chars().filter(|c| c.is_alphabetic()).count() > 6)
            .count() as f32;
        let total_words = text.split_whitespace().count() as f32;
        
        let complex_word_ratio = if total_words > 0.0 { long_words / total_words } else { 0.0 };
        let sentence_complexity = (avg_sentence_length / 15.0).min(1.0); // Normalize to 0-1
        
        ((complex_word_ratio + sentence_complexity) / 2.0 * 10.0).min(10.0)
    }

    fn calculate_reading_level(text: &str, avg_sentence_length: f32, complexity: f32) -> super::ReadingLevel {
        // Simplified Flesch-Kincaid calculation
        let syllable_count = Self::estimate_syllables(text);
        let word_count = text.split_whitespace().count() as f32;
        let sentence_count = text.matches(&['.', '!', '?'][..]).count() as f32;
        
        let flesch_kincaid = if sentence_count > 0.0 && word_count > 0.0 {
            206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
        } else {
            50.0
        };

        let grade_level = Self::flesch_to_grade(flesch_kincaid);
        
        super::ReadingLevel {
            flesch_kincaid: flesch_kincaid.max(0.0).min(100.0),
            gunning_fog: (avg_sentence_length * 0.4 + complexity).min(20.0),
            coleman_liau: (complexity * 1.2 + 5.0).min(20.0),
            grade_level,
            complexity_score: complexity,
        }
    }

    fn calculate_quality_scores(text: &str, word_count: u32) -> super::WritingQuality {
        let text_lower = text.to_lowercase();
        
        // Clarity score based on sentence structure and word choice
        let clarity = Self::calculate_clarity(&text_lower, word_count);
        
        // Coherence based on transition words and paragraph structure
        let coherence = Self::calculate_coherence(&text_lower);
        
        // Grammar score (simplified)
        let grammar = Self::estimate_grammar_quality(text);
        
        // Vocabulary diversity
        let vocab_diversity = Self::calculate_vocabulary_diversity(text);
        
        // Sentence variety
        let sentence_variety = Self::calculate_sentence_variety(text);

        super::WritingQuality {
            clarity_score: clarity,
            coherence_score: coherence,
            grammar_score: grammar,
            vocabulary_diversity: vocab_diversity,
            sentence_variety,
        }
    }

    fn analyze_linguistic_features(text: &str, avg_sentence_length: f32) -> super::LinguisticFeatures {
        let passive_voice_ratio = Self::estimate_passive_voice(text);
        let transition_words = Self::count_transition_words(text);
        let academic_vocab_ratio = Self::calculate_academic_vocabulary_ratio(text);
        let complex_sentences_ratio = Self::estimate_complex_sentences(text);

        super::LinguisticFeatures {
            average_sentence_length: avg_sentence_length,
            passive_voice_ratio,
            transition_words_count: transition_words,
            academic_vocabulary_ratio: academic_vocab_ratio,
            complex_sentences_ratio,
        }
    }

    fn analyze_structure(text: &str) -> super::StructureAnalysis {
        let has_introduction = Self::has_introduction(text);
        let has_conclusion = Self::has_conclusion(text);
        let paragraph_coherence = Self::calculate_paragraph_coherence(text);
        let topic_consistency = Self::calculate_topic_consistency(text);
        let logical_flow = Self::calculate_logical_flow(text);

        super::StructureAnalysis {
            has_introduction,
            has_conclusion,
            paragraph_coherence,
            topic_consistency,
            logical_flow,
        }
    }

    fn analyze_content(text: &str, word_count: u32) -> super::ContentMetrics {
        let originality = Self::estimate_originality(text);
        let depth = Self::calculate_depth_of_analysis(text, word_count);
        let evidence_usage = Self::calculate_evidence_usage(text);
        let critical_thinking = Self::estimate_critical_thinking(text);
        let argument_strength = Self::calculate_argument_strength(text);

        super::ContentMetrics {
            originality_score: originality,
            depth_of_analysis: depth,
            evidence_usage,
            critical_thinking,
            argument_strength,
        }
    }

    // Helper methods for analysis calculations
    fn estimate_syllables(text: &str) -> f32 {
        text.split_whitespace()
            .map(|word| {
                let clean_word = word.chars().filter(|c| c.is_alphabetic()).collect::<String>();
                let vowel_count = clean_word.chars()
                    .filter(|&c| "aeiouAEIOU".contains(c))
                    .count();
                vowel_count.max(1) as f32 // At least 1 syllable per word
            })
            .sum()
    }

    fn flesch_to_grade(flesch: f32) -> String {
        match flesch as i32 {
            90..=100 => "5th grade".to_string(),
            80..=89 => "6th grade".to_string(),
            70..=79 => "7th grade".to_string(),
            60..=69 => "8th-9th grade".to_string(),
            50..=59 => "10th-12th grade".to_string(),
            30..=49 => "College level".to_string(),
            _ => "Graduate level".to_string(),
        }
    }

    fn calculate_clarity(text: &str, word_count: u32) -> f32 {
        let simple_words = text.split_whitespace()
            .filter(|word| word.len() <= 6)
            .count() as f32;
        let clarity_ratio = simple_words / word_count as f32;
        (clarity_ratio * 10.0 + 3.0).min(10.0)
    }

    fn calculate_coherence(text: &str) -> f32 {
        let transition_words = ["however", "therefore", "furthermore", "moreover", "consequently", "additionally"];
        let transition_count = transition_words.iter()
            .map(|&word| text.matches(word).count())
            .sum::<usize>() as f32;
        
        let paragraphs = text.split("\n\n").count() as f32;
        let coherence_score = if paragraphs > 1.0 {
            ((transition_count / paragraphs) * 3.0 + 5.0).min(10.0)
        } else {
            6.0
        };
        
        coherence_score
    }

    fn estimate_grammar_quality(text: &str) -> f32 {
        // Simplified grammar scoring based on common patterns
        let sentences = text.split(&['.', '!', '?'][..]).count() as f32;
        let capital_starts = text.lines()
            .filter(|line| line.chars().next().map_or(false, |c| c.is_uppercase()))
            .count() as f32;
        
        let grammar_ratio = if sentences > 0.0 { capital_starts / sentences } else { 0.5 };
        (grammar_ratio * 8.0 + 2.0).min(10.0)
    }

    fn calculate_vocabulary_diversity(text: &str) -> f32 {
        let words: Vec<&str> = text.split_whitespace().collect();
        let unique_words: std::collections::HashSet<&str> = words.iter().cloned().collect();
        
        if words.is_empty() {
            return 5.0;
        }
        
        let diversity_ratio = unique_words.len() as f32 / words.len() as f32;
        (diversity_ratio * 15.0).min(10.0)
    }

    fn calculate_sentence_variety(text: &str) -> f32 {
        let sentences: Vec<&str> = text.split(&['.', '!', '?'][..]).collect();
        let lengths: Vec<usize> = sentences.iter()
            .map(|s| s.split_whitespace().count())
            .collect();
        
        if lengths.is_empty() {
            return 5.0;
        }
        
        let mean = lengths.iter().sum::<usize>() as f32 / lengths.len() as f32;
        let variance = lengths.iter()
            .map(|&len| (len as f32 - mean).powi(2))
            .sum::<f32>() / lengths.len() as f32;
        
        (variance.sqrt() * 0.5 + 5.0).min(10.0)
    }

    fn estimate_passive_voice(text: &str) -> f32 {
        let passive_indicators = ["was", "were", "been", "being"];
        let total_verbs = text.split_whitespace()
            .filter(|word| word.ends_with("ed") || passive_indicators.contains(&word.to_lowercase().as_str()))
            .count() as f32;
        
        let passive_count = passive_indicators.iter()
            .map(|&indicator| text.to_lowercase().matches(indicator).count())
            .sum::<usize>() as f32;
        
        if total_verbs > 0.0 {
            passive_count / total_verbs
        } else {
            0.1
        }
    }

    fn count_transition_words(text: &str) -> u32 {
        let transitions = [
            "however", "therefore", "furthermore", "moreover", "consequently",
            "additionally", "meanwhile", "nevertheless", "thus", "hence"
        ];
        
        transitions.iter()
            .map(|&word| text.to_lowercase().matches(word).count())
            .sum::<usize>() as u32
    }

    fn calculate_academic_vocabulary_ratio(text: &str) -> f32 {
        let academic_words = [
            "analyze", "synthesize", "evaluate", "demonstrate", "investigate",
            "hypothesis", "methodology", "significant", "furthermore", "consequently"
        ];
        
        let academic_count = academic_words.iter()
            .map(|&word| text.to_lowercase().matches(word).count())
            .sum::<usize>() as f32;
        
        let total_words = text.split_whitespace().count() as f32;
        
        if total_words > 0.0 {
            (academic_count / total_words * 100.0).min(1.0)
        } else {
            0.0
        }
    }

    fn estimate_complex_sentences(text: &str) -> f32 {
        let conjunctions = ["because", "although", "since", "while", "whereas", "unless"];
        let complex_count = conjunctions.iter()
            .map(|&conj| text.to_lowercase().matches(conj).count())
            .sum::<usize>() as f32;
        
        let total_sentences = text.matches(&['.', '!', '?'][..]).count() as f32;
        
        if total_sentences > 0.0 {
            complex_count / total_sentences
        } else {
            0.3
        }
    }

    fn has_introduction(text: &str) -> bool {
        let first_paragraph = text.split("\n\n").next().unwrap_or("");
        let intro_indicators = ["introduction", "this paper", "this essay", "this study"];
        
        intro_indicators.iter().any(|&indicator| 
            first_paragraph.to_lowercase().contains(indicator)
        ) || first_paragraph.len() > 100
    }

    fn has_conclusion(text: &str) -> bool {
        let paragraphs: Vec<&str> = text.split("\n\n").collect();
        if let Some(last_paragraph) = paragraphs.last() {
            let conclusion_indicators = ["conclusion", "in summary", "to conclude", "finally"];
            conclusion_indicators.iter().any(|&indicator| 
                last_paragraph.to_lowercase().contains(indicator)
            )
        } else {
            false
        }
    }

    fn calculate_paragraph_coherence(text: &str) -> f32 {
        let paragraphs: Vec<&str> = text.split("\n\n").collect();
        if paragraphs.len() <= 1 {
            return 7.0;
        }
        
        // Simple coherence based on paragraph length consistency
        let lengths: Vec<usize> = paragraphs.iter().map(|p| p.len()).collect();
        let mean_length = lengths.iter().sum::<usize>() as f32 / lengths.len() as f32;
        let variance = lengths.iter()
            .map(|&len| (len as f32 - mean_length).powi(2))
            .sum::<f32>() / lengths.len() as f32;
        
        (10.0 - (variance.sqrt() / mean_length * 5.0)).max(3.0)
    }

    fn calculate_topic_consistency(_text: &str) -> f32 {
        // Simplified topic consistency - would use NLP in real implementation
        7.5
    }

    fn calculate_logical_flow(_text: &str) -> f32 {
        // Simplified logical flow - would use more sophisticated analysis
        7.0
    }

    fn estimate_originality(_text: &str) -> f32 {
        // Simplified originality estimation
        6.5
    }

    fn calculate_depth_of_analysis(text: &str, word_count: u32) -> f32 {
        let analysis_words = ["analyze", "examine", "investigate", "explore", "evaluate", "assess"];
        let analysis_count = analysis_words.iter()
            .map(|&word| text.to_lowercase().matches(word).count())
            .sum::<usize>() as f32;
        
        let depth_ratio = analysis_count / (word_count as f32 / 100.0);
        (depth_ratio * 2.0 + 5.0).min(10.0)
    }

    fn calculate_evidence_usage(text: &str) -> f32 {
        let evidence_indicators = ["according to", "research shows", "studies indicate", "evidence suggests"];
        let evidence_count = evidence_indicators.iter()
            .map(|&indicator| text.to_lowercase().matches(indicator).count())
            .sum::<usize>() as f32;
        
        (evidence_count * 2.0 + 4.0).min(10.0)
    }

    fn estimate_critical_thinking(text: &str) -> f32 {
        let critical_words = ["however", "although", "despite", "on the contrary", "nevertheless"];
        let critical_count = critical_words.iter()
            .map(|&word| text.to_lowercase().matches(word).count())
            .sum::<usize>() as f32;
        
        (critical_count * 1.5 + 5.0).min(10.0)
    }

    fn calculate_argument_strength(text: &str) -> f32 {
        let argument_words = ["therefore", "thus", "consequently", "because", "since"];
        let argument_count = argument_words.iter()
            .map(|&word| text.to_lowercase().matches(word).count())
            .sum::<usize>() as f32;
        
        (argument_count * 1.8 + 4.5).min(10.0)
    }
}