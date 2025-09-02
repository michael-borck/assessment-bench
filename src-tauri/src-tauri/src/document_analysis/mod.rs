use serde::{Serialize, Deserialize};

pub mod client;
pub mod models;

pub use client::DocumentLensClient;
pub use models::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DocumentAnalysis {
    pub word_count: u32,
    pub sentence_count: u32,
    pub paragraph_count: u32,
    pub reading_level: ReadingLevel,
    pub writing_quality: WritingQuality,
    pub linguistic_features: LinguisticFeatures,
    pub structure_analysis: StructureAnalysis,
    pub content_metrics: ContentMetrics,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReadingLevel {
    pub flesch_kincaid: f32,
    pub gunning_fog: f32,
    pub coleman_liau: f32,
    pub grade_level: String,
    pub complexity_score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WritingQuality {
    pub clarity_score: f32,
    pub coherence_score: f32,
    pub grammar_score: f32,
    pub vocabulary_diversity: f32,
    pub sentence_variety: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LinguisticFeatures {
    pub average_sentence_length: f32,
    pub passive_voice_ratio: f32,
    pub transition_words_count: u32,
    pub academic_vocabulary_ratio: f32,
    pub complex_sentences_ratio: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StructureAnalysis {
    pub has_introduction: bool,
    pub has_conclusion: bool,
    pub paragraph_coherence: f32,
    pub topic_consistency: f32,
    pub logical_flow: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ContentMetrics {
    pub originality_score: f32,
    pub depth_of_analysis: f32,
    pub evidence_usage: f32,
    pub critical_thinking: f32,
    pub argument_strength: f32,
}

impl DocumentAnalysis {
    pub fn to_formatted_string(&self) -> String {
        format!(
            r#"DOCUMENT ANALYSIS SUMMARY:

Basic Metrics:
- Word Count: {}
- Sentence Count: {}  
- Paragraph Count: {}

Reading Level:
- Flesch-Kincaid: {:.1} (Grade Level: {})
- Gunning Fog Index: {:.1}
- Coleman-Liau: {:.1}
- Overall Complexity: {:.1}/10

Writing Quality:
- Clarity: {:.1}/10
- Coherence: {:.1}/10  
- Grammar: {:.1}/10
- Vocabulary Diversity: {:.1}/10
- Sentence Variety: {:.1}/10

Linguistic Features:
- Average Sentence Length: {:.1} words
- Passive Voice Usage: {:.1}%
- Transition Words: {}
- Academic Vocabulary: {:.1}%
- Complex Sentences: {:.1}%

Structure Analysis:
- Has Introduction: {}
- Has Conclusion: {}
- Paragraph Coherence: {:.1}/10
- Topic Consistency: {:.1}/10
- Logical Flow: {:.1}/10

Content Quality:
- Originality: {:.1}/10
- Depth of Analysis: {:.1}/10
- Evidence Usage: {:.1}/10
- Critical Thinking: {:.1}/10
- Argument Strength: {:.1}/10"#,
            self.word_count,
            self.sentence_count,
            self.paragraph_count,
            self.reading_level.flesch_kincaid,
            self.reading_level.grade_level,
            self.reading_level.gunning_fog,
            self.reading_level.coleman_liau,
            self.reading_level.complexity_score,
            self.writing_quality.clarity_score,
            self.writing_quality.coherence_score,
            self.writing_quality.grammar_score,
            self.writing_quality.vocabulary_diversity,
            self.writing_quality.sentence_variety,
            self.linguistic_features.average_sentence_length,
            self.linguistic_features.passive_voice_ratio * 100.0,
            self.linguistic_features.transition_words_count,
            self.linguistic_features.academic_vocabulary_ratio * 100.0,
            self.linguistic_features.complex_sentences_ratio * 100.0,
            if self.structure_analysis.has_introduction { "Yes" } else { "No" },
            if self.structure_analysis.has_conclusion { "Yes" } else { "No" },
            self.structure_analysis.paragraph_coherence,
            self.structure_analysis.topic_consistency,
            self.structure_analysis.logical_flow,
            self.content_metrics.originality_score,
            self.content_metrics.depth_of_analysis,
            self.content_metrics.evidence_usage,
            self.content_metrics.critical_thinking,
            self.content_metrics.argument_strength
        )
    }

    pub fn overall_score(&self) -> f32 {
        let quality_avg = (self.writing_quality.clarity_score + 
                          self.writing_quality.coherence_score + 
                          self.writing_quality.grammar_score) / 3.0;
        
        let structure_avg = (self.structure_analysis.paragraph_coherence + 
                            self.structure_analysis.topic_consistency + 
                            self.structure_analysis.logical_flow) / 3.0;
        
        let content_avg = (self.content_metrics.depth_of_analysis + 
                          self.content_metrics.evidence_usage + 
                          self.content_metrics.critical_thinking + 
                          self.content_metrics.argument_strength) / 4.0;
        
        (quality_avg + structure_avg + content_avg) / 3.0
    }
}