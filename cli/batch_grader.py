#!/usr/bin/env python3
"""
AI Assessor CLI - Batch Processing Tool

This CLI tool enables researchers to perform automated grading operations
on multiple student submissions using different workflows and configurations.

Usage:
    python batch_grader.py grade --directory /path/to/submissions --config config.json
    python batch_grader.py analyze --file essay.docx --workflow enhanced
    python batch_grader.py compare --workflows basic,enhanced --directory /path/to/submissions
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

@dataclass
class GradingConfig:
    """Configuration for grading operations"""
    workflow: str = 'basic'  # 'basic' or 'enhanced'
    provider: str = 'openai'
    model: str = 'gpt-4-turbo'
    temperature: float = 0.7
    system_prompt: str = ''
    user_prompt: str = ''
    rubric_path: Optional[str] = None
    marking_guide_path: Optional[str] = None
    guidelines_path: Optional[str] = None
    assignment_spec_path: Optional[str] = None
    document_analysis_url: str = 'http://localhost:8001'
    max_workers: int = 3
    output_format: str = 'json'  # 'json', 'csv', 'txt'

@dataclass
class SubmissionResult:
    """Result of grading a single submission"""
    file_path: str
    student_name: str
    workflow: str
    provider: str
    grade: Optional[str] = None
    feedback: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    analysis_time: Optional[float] = None
    grading_time: Optional[float] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None

class BatchGrader:
    def __init__(self, config: GradingConfig):
        self.config = config
        self.results: List[SubmissionResult] = []
        
    def load_support_files(self) -> Dict[str, str]:
        """Load all support files into memory"""
        support_files = {}
        
        for file_type in ['rubric', 'marking_guide', 'guidelines', 'assignment_spec']:
            path_attr = f"{file_type}_path"
            file_path = getattr(self.config, path_attr)
            
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        support_files[file_type] = f.read()
                    print(f"✓ Loaded {file_type}: {file_path}")
                except Exception as e:
                    print(f"✗ Failed to load {file_type} from {file_path}: {e}")
            else:
                if file_type in ['rubric', 'marking_guide', 'guidelines']:
                    print(f"⚠ Required file missing: {file_type}")
                    
        return support_files
    
    def analyze_document(self, content: str) -> Optional[Dict[str, Any]]:
        """Analyze document using the document analysis API"""
        if self.config.workflow != 'enhanced':
            return None
            
        try:
            response = requests.post(
                f"{self.config.document_analysis_url}/analyze",
                json={
                    "content": content,
                    "expectedCitationStyle": "APA"
                },
                timeout=30
            )
            
            if response.ok:
                return response.json().get('metrics')
            else:
                print(f"⚠ Document analysis failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠ Document analysis error: {e}")
            return None
    
    def grade_submission(self, file_path: str, support_files: Dict[str, str]) -> SubmissionResult:
        """Grade a single submission file"""
        start_time = time.time()
        
        # Extract student name from filename
        student_name = Path(file_path).stem
        
        result = SubmissionResult(
            file_path=file_path,
            student_name=student_name,
            workflow=self.config.workflow,
            provider=self.config.provider,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        try:
            # Read submission content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            analysis_start = time.time()
            
            # Perform document analysis if enhanced workflow
            metrics = None
            if self.config.workflow == 'enhanced':
                metrics = self.analyze_document(content)
                result.metrics = metrics
                
            result.analysis_time = time.time() - analysis_start
            
            # Prepare grading prompt
            grading_prompt = self.build_grading_prompt(
                content, support_files, metrics
            )
            
            # Simulate LLM grading (replace with actual LLM API call)
            grading_start = time.time()
            grade, feedback = self.call_llm_grading(grading_prompt)
            result.grading_time = time.time() - grading_start
            
            result.grade = grade
            result.feedback = feedback
            
            print(f"✓ Graded {student_name} - Grade: {grade}")
            
        except Exception as e:
            result.error = str(e)
            print(f"✗ Failed to grade {student_name}: {e}")
            
        return result
    
    def build_grading_prompt(self, content: str, support_files: Dict[str, str], 
                           metrics: Optional[Dict[str, Any]] = None) -> str:
        """Build the complete grading prompt"""
        prompt_parts = []
        
        # System prompt
        if self.config.system_prompt:
            prompt_parts.append(f"SYSTEM: {self.config.system_prompt}")
            
        # Add support files
        for file_type, file_content in support_files.items():
            prompt_parts.append(f"\n--- {file_type.upper().replace('_', ' ')} ---\n{file_content}")
            
        # Add document analysis if available
        if metrics and self.config.workflow == 'enhanced':
            prompt_parts.append(self.format_analysis_for_prompt(metrics))
            
        # Add submission content
        prompt_parts.append(f"\n--- STUDENT SUBMISSION ---\n{content}")
        
        # Add user prompt
        if self.config.user_prompt:
            prompt_parts.append(f"\n{self.config.user_prompt}")
        else:
            prompt_parts.append(
                "\nPlease grade this submission according to the rubric and provide detailed feedback."
            )
            
        return "\n".join(prompt_parts)
    
    def format_analysis_for_prompt(self, metrics: Dict[str, Any]) -> str:
        """Format analysis metrics for the LLM prompt"""
        return f"""
--- DOCUMENT ANALYSIS ---
Word Count: {metrics.get('wordCount', 'N/A')}
Reading Level: Grade {metrics.get('fleschKincaidGradeLevel', 'N/A')}
Readability Score: {metrics.get('fleschReadingEase', 'N/A')}
Citations Found: {metrics.get('citationCount', 'N/A')}
Grammar Score: {metrics.get('grammarScore', 'N/A')}%
Structure Score: {metrics.get('structuralCoherence', 'N/A')}%

Please incorporate these metrics into your grading assessment.
"""
    
    def call_llm_grading(self, prompt: str) -> tuple[str, str]:
        """Call LLM API for grading (placeholder - implement actual API calls)"""
        # This is a placeholder - in real implementation, this would call
        # the appropriate LLM API (OpenAI, Anthropic, etc.)
        
        # Simulate processing time
        time.sleep(1)
        
        # Return mock grade and feedback
        return "B+", f"Mock feedback for submission. Analyzed {len(prompt)} characters of prompt."
    
    def process_directory(self, directory_path: str) -> List[SubmissionResult]:
        """Process all files in a directory"""
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
            
        # Find all supported files
        supported_extensions = ['.txt', '.docx', '.doc', '.pdf']
        files = []
        for ext in supported_extensions:
            files.extend(directory.glob(f"*{ext}"))
            
        if not files:
            print(f"⚠ No supported files found in {directory_path}")
            return []
            
        print(f"Found {len(files)} files to process")
        
        # Load support files once
        support_files = self.load_support_files()
        required_files = ['rubric', 'marking_guide', 'guidelines']
        missing_required = [f for f in required_files if f not in support_files]
        
        if missing_required:
            raise ValueError(f"Missing required support files: {missing_required}")
        
        # Process files in parallel
        results = []
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_file = {
                executor.submit(self.grade_submission, str(file), support_files): file
                for file in files
            }
            
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"✗ Error processing {file}: {e}")
                    
        self.results = results
        return results
    
    def save_results(self, output_path: str) -> None:
        """Save results in specified format"""
        output_path = Path(output_path)
        
        if self.config.output_format == 'json':
            with open(output_path.with_suffix('.json'), 'w') as f:
                json.dump([asdict(r) for r in self.results], f, indent=2)
                
        elif self.config.output_format == 'csv':
            with open(output_path.with_suffix('.csv'), 'w', newline='') as f:
                if self.results:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.results[0]).keys())
                    writer.writeheader()
                    for result in self.results:
                        writer.writerow(asdict(result))
                        
        elif self.config.output_format == 'txt':
            with open(output_path.with_suffix('.txt'), 'w') as f:
                for result in self.results:
                    f.write(f"=== {result.student_name} ===\n")
                    f.write(f"Grade: {result.grade}\n")
                    f.write(f"Workflow: {result.workflow}\n")
                    f.write(f"Feedback:\n{result.feedback}\n\n")
                    
        print(f"✓ Results saved to {output_path}")

def load_config(config_path: str) -> GradingConfig:
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return GradingConfig()
        
    with open(config_path, 'r') as f:
        data = json.load(f)
        
    return GradingConfig(**data)

def main():
    parser = argparse.ArgumentParser(description="AI Assessor CLI - Batch Processing Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Grade command
    grade_parser = subparsers.add_parser('grade', help='Grade submissions in batch')
    grade_parser.add_argument('--directory', required=True, help='Directory containing submissions')
    grade_parser.add_argument('--config', help='Configuration file path')
    grade_parser.add_argument('--output', default='results', help='Output file path')
    grade_parser.add_argument('--workflow', choices=['basic', 'enhanced'], default='basic')
    
    # Analyze command  
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single submission')
    analyze_parser.add_argument('--file', required=True, help='Submission file to analyze')
    analyze_parser.add_argument('--workflow', choices=['basic', 'enhanced'], default='enhanced')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare different workflows')
    compare_parser.add_argument('--directory', required=True, help='Directory containing submissions')
    compare_parser.add_argument('--workflows', default='basic,enhanced', help='Comma-separated workflows')
    compare_parser.add_argument('--output', default='comparison', help='Output file path')
    
    # Generate config command
    config_parser = subparsers.add_parser('init', help='Generate sample configuration file')
    config_parser.add_argument('--output', default='config.json', help='Output config file')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        sample_config = asdict(GradingConfig())
        with open(args.output, 'w') as f:
            json.dump(sample_config, f, indent=2)
        print(f"✓ Sample configuration created: {args.output}")
        return
        
    if not args.command:
        parser.print_help()
        return
        
    # Load configuration
    config = GradingConfig()
    if hasattr(args, 'config') and args.config:
        config = load_config(args.config)
        
    if hasattr(args, 'workflow'):
        config.workflow = args.workflow
        
    if args.command == 'grade':
        grader = BatchGrader(config)
        results = grader.process_directory(args.directory)
        grader.save_results(args.output)
        
        # Print summary
        total = len(results)
        successful = len([r for r in results if not r.error])
        failed = total - successful
        
        print(f"\n=== GRADING SUMMARY ===")
        print(f"Total submissions: {total}")
        print(f"Successfully graded: {successful}")
        print(f"Failed: {failed}")
        
        if successful > 0:
            avg_time = sum(r.grading_time or 0 for r in results if r.grading_time) / successful
            print(f"Average grading time: {avg_time:.2f}s")
            
    elif args.command == 'analyze':
        # Single file analysis
        grader = BatchGrader(config)
        support_files = grader.load_support_files()
        result = grader.grade_submission(args.file, support_files)
        
        print(f"\n=== ANALYSIS RESULT ===")
        print(f"File: {result.file_path}")
        print(f"Grade: {result.grade}")
        print(f"Workflow: {result.workflow}")
        if result.metrics:
            print(f"Analysis metrics available: {len(result.metrics)} metrics")
        print(f"Feedback:\n{result.feedback}")
        
    elif args.command == 'compare':
        workflows = args.workflows.split(',')
        comparison_results = {}
        
        for workflow in workflows:
            config.workflow = workflow.strip()
            grader = BatchGrader(config)
            results = grader.process_directory(args.directory)
            comparison_results[workflow] = results
            
        # Save comparison results
        with open(f"{args.output}_comparison.json", 'w') as f:
            json.dump({
                workflow: [asdict(r) for r in results]
                for workflow, results in comparison_results.items()
            }, f, indent=2)
            
        print(f"✓ Comparison results saved to {args.output}_comparison.json")

if __name__ == '__main__':
    main()