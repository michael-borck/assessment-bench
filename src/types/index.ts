// Core application types

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  config: ProjectConfig;
}

export interface ProjectConfig {
  tiers_enabled: GradingTier[];
  providers: LLMProvider[];
  repetitions: number;
  document_lens_url?: string;
}

export type GradingTier = 'basic' | 'enhanced' | 'assignment-aware';

export interface LLMProvider {
  id: string;
  name: string;
  type: 'openai' | 'anthropic' | 'google' | 'ollama' | 'custom';
  config: LLMProviderConfig;
}

export interface LLMProviderConfig {
  api_key?: string;
  base_url?: string;
  model: string;
  temperature: number;
  max_tokens?: number;
}

export interface Submission {
  id: string;
  project_id: string;
  original_filename: string;
  file_hash: string;
  imported_at: string;
  file_type: 'pdf' | 'docx' | 'txt' | 'md';
  word_count: number;
  status: 'pending' | 'processing' | 'processed' | 'error';
  extracted_text?: string;
  analysis_cache?: DocumentAnalysis;
}

export interface DocumentAnalysis {
  // Basic text metrics
  word_count: number;
  sentence_count: number;
  paragraph_count: number;
  
  // Readability scores
  flesch_reading_ease?: number;
  flesch_kincaid_grade?: number;
  
  // Writing quality metrics
  passive_voice_percentage?: number;
  sentence_variety_score?: number;
  vocabulary_richness?: number;
  
  // Academic analysis (Tier 3)
  citations?: Citation[];
  ai_detection_score?: number;
  plagiarism_indicators?: string[];
  reference_integrity?: ReferenceCheck[];
}

export interface Citation {
  text: string;
  style: string;
  doi?: string;
  url?: string;
  verified: boolean;
}

export interface ReferenceCheck {
  citation: string;
  status: 'valid' | 'invalid' | 'warning';
  message?: string;
}

export interface GradingResult {
  id: string;
  submission_id: string;
  provider_id: string;
  tier: GradingTier;
  run_number: number;
  created_at: string;
  
  // Raw response
  raw_response: string;
  
  // Extracted scores
  overall_grade?: string;
  total_points?: number;
  rubric_scores: RubricScore[];
  
  // Feedback
  summary_feedback?: string;
  strengths: string[];
  improvements: string[];
  
  // Validation
  validation_result: ValidationResult;
}

export interface RubricScore {
  criterion: string;
  points_awarded: number;
  points_possible: number;
  comments?: string;
}

export interface ValidationResult {
  is_valid: boolean;
  confidence: number; // 0-1 scale
  issues: ValidationIssue[];
  extracted_grade?: string;
  calculated_total?: number;
}

export interface ValidationIssue {
  type: 'GRADE_MISMATCH' | 'MISSING_RUBRIC_SCORE' | 'CALCULATION_ERROR';
  severity: 'WARNING' | 'ERROR';
  description: string;
  suggested_fix?: string;
}

export interface AggregatedResult {
  submission_id: string;
  provider_id: string;
  tier: GradingTier;
  
  // Statistical measures
  mean_score: number;
  median_score: number;
  std_deviation: number;
  coefficient_of_variation: number;
  
  // Individual results
  individual_results: GradingResult[];
  
  // Aggregated feedback
  consensus_feedback?: string;
  common_strengths: string[];
  common_improvements: string[];
}

export interface Rubric {
  id: string;
  name: string;
  description?: string;
  criteria: RubricCriterion[];
  total_points: number;
}

export interface RubricCriterion {
  id: string;
  name: string;
  description: string;
  points_possible: number;
  levels?: RubricLevel[];
}

export interface RubricLevel {
  name: string;
  description: string;
  points: number;
}