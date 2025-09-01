#!/usr/bin/env python3
"""
Example usage of the AI Assessor CLI for research studies.

This script demonstrates how to set up and run comparative grading studies
using the batch processing capabilities.
"""

import os
import json
from pathlib import Path
import subprocess
import time

def setup_example_study():
    """Set up an example research study structure"""
    
    # Create directory structure
    study_dir = Path("example_study")
    study_dir.mkdir(exist_ok=True)
    
    submissions_dir = study_dir / "submissions"
    submissions_dir.mkdir(exist_ok=True)
    
    support_files_dir = study_dir / "support_files"
    support_files_dir.mkdir(exist_ok=True)
    
    results_dir = study_dir / "results"
    results_dir.mkdir(exist_ok=True)
    
    # Create sample submissions
    sample_essays = {
        "alice_johnson.txt": """
The Impact of Climate Change on Arctic Wildlife

Introduction
Climate change represents one of the most significant environmental challenges of our time. The Arctic region, in particular, has experienced dramatic changes that have profound implications for wildlife populations. This essay examines the various ways in which climate change affects Arctic wildlife, focusing on polar bears, seals, and arctic birds.

Effects on Polar Bears
Polar bears have become the iconic symbol of climate change impacts. As sea ice diminishes due to rising temperatures, polar bears lose their primary hunting grounds. The reduced ice coverage forces these apex predators to travel greater distances to find food, leading to malnutrition and decreased reproductive success. Studies have shown a significant decline in polar bear populations across several Arctic regions.

Impact on Seal Populations
Seals, which serve as the primary food source for polar bears, are also affected by changing ice conditions. Ring seals require stable sea ice for breeding and pupping. The earlier breakup of sea ice disrupts their reproductive cycles and reduces pup survival rates. This creates a cascading effect throughout the Arctic food web.

Arctic Bird Species
Migratory bird species that depend on Arctic breeding grounds face multiple challenges. Changes in vegetation patterns, insect populations, and weather conditions affect their feeding and nesting success. Some species are shifting their migration patterns, while others face population declines.

Conclusion
The evidence clearly demonstrates that climate change poses significant threats to Arctic wildlife. Immediate action is required to mitigate these impacts and protect these vulnerable ecosystems for future generations.

References
Jones, M. (2020). Arctic Wildlife and Climate Change. Environmental Science Journal, 45(3), 123-145.
Smith, R. (2019). Polar Bear Population Dynamics. Arctic Research Quarterly, 12(4), 67-89.
        """,
        
        "bob_miller.txt": """
Climate Change Effects on Arctic Animals

Climate change is bad for arctic animals. The ice is melting and this makes it hard for polar bears to hunt. They need ice to catch seals but there is less ice now.

Seals also have problems. They cant make their homes on the ice anymore. The ice breaks up too early and their babies die.

Birds are also affected. They cant find the right food and places to nest. Many birds are leaving the arctic or dying.

In conclusion climate change is really bad for arctic animals. We need to do something about it or all the animals will die. The government should make laws to stop pollution and save the animals.

This shows that climate change is a serious problem that affects many animals in the arctic.
        """,
        
        "carol_davis.txt": """
Arctic Wildlife and the Changing Climate: A Comprehensive Analysis

Abstract
This comprehensive analysis examines the multifaceted impacts of anthropogenic climate change on Arctic wildlife populations. Through systematic review of recent scientific literature and analysis of longitudinal population data, this study identifies critical vulnerabilities in Arctic ecosystems and proposes evidence-based conservation strategies.

Introduction
The Arctic region has experienced temperature increases twice the global average, a phenomenon known as Arctic amplification (Peterson et al., 2021). This rapid environmental change has created unprecedented challenges for wildlife species adapted to stable ice conditions and predictable seasonal patterns. Understanding these impacts is crucial for developing effective conservation strategies and informing climate policy decisions.

Literature Review
Extensive research has documented the relationship between declining sea ice extent and polar bear (Ursus maritimus) population dynamics. Stirling and Derocher (2012) demonstrated significant correlations between ice-free periods and reduced body condition in adult females. Subsequent studies by Hamilton et al. (2020) confirmed decreased denning success rates across multiple subpopulations.

Methodology
This analysis synthesized data from 47 peer-reviewed studies published between 2015-2023, focusing on three key species groups: marine mammals, terrestrial mammals, and avian species. Population trend analysis utilized regression modeling to identify statistically significant changes over time.

Results and Analysis
Marine mammal populations showed the strongest negative correlations with ice loss metrics (r = -0.73, p < 0.001). Ringed seals (Pusa hispida) demonstrated particularly severe reproductive impacts, with pup survival rates declining by 34% over the study period. Arctic foxes (Vulpes lagopus) exhibited complex responses, with some populations declining due to prey reduction while others expanded ranges northward.

Avian species responses varied significantly by ecological niche. Specialized Arctic breeders like the Ivory Gull (Pagophila eburnea) showed steep population declines (-67% over 20 years), while more adaptable species demonstrated range shifts rather than population collapse.

Discussion
The differential species responses highlight the importance of ecological specialization in determining vulnerability to climate change. Species with narrow habitat requirements and limited dispersal abilities face the greatest extinction risk. Conversely, generalist species may benefit from reduced competition and expanded suitable habitat.

Conservation Implications
Effective conservation strategies must address both direct climate impacts and indirect effects through food web disruption. Protecting critical habitat areas, establishing climate corridors, and reducing non-climate stressors represent priority actions. International cooperation through the Arctic Council framework provides the best opportunity for coordinated conservation efforts.

Conclusions
Arctic wildlife faces unprecedented challenges from rapid climate change. While some species demonstrate adaptive capacity, many specialized Arctic fauna require immediate conservation intervention to prevent local extinctions. The cascading effects of these changes will likely persist for decades, regardless of future emission scenarios.

Recommendations for future research include expanded monitoring of understudied species, investigation of evolutionary adaptation potential, and development of predictive models for conservation planning.

References
[Contains 23 academic references in proper APA format]
        """
    }
    
    # Write sample submissions
    for filename, content in sample_essays.items():
        with open(submissions_dir / filename, 'w') as f:
            f.write(content.strip())
    
    # Create sample support files
    support_files = {
        "rubric.txt": """
ENVIRONMENTAL SCIENCE ESSAY RUBRIC

CRITERION 1: THESIS AND ARGUMENT CLARITY (20 points)
Excellent (18-20): Clear, compelling thesis with sophisticated argument structure
Good (15-17): Clear thesis with well-developed arguments
Satisfactory (12-14): Thesis present but arguments lack depth
Needs Improvement (0-11): Unclear or missing thesis

CRITERION 2: EVIDENCE AND SOURCES (25 points)
Excellent (23-25): Multiple credible sources, excellent integration
Good (19-22): Good use of credible sources with proper integration
Satisfactory (15-18): Adequate sources but limited integration
Needs Improvement (0-14): Few or poor quality sources

CRITERION 3: SCIENTIFIC ACCURACY (20 points)
Excellent (18-20): Scientifically accurate throughout, demonstrates deep understanding
Good (15-17): Mostly accurate with minor errors
Satisfactory (12-14): Generally accurate but some misconceptions
Needs Improvement (0-11): Significant scientific errors

CRITERION 4: ORGANIZATION AND FLOW (15 points)
Excellent (14-15): Clear structure with smooth transitions
Good (12-13): Well organized with adequate transitions
Satisfactory (9-11): Basic organization, some unclear connections
Needs Improvement (0-8): Poor organization, difficult to follow

CRITERION 5: WRITING QUALITY (20 points)
Excellent (18-20): Clear, engaging prose with varied sentence structure
Good (15-17): Clear writing with minor issues
Satisfactory (12-14): Adequate clarity but some awkward constructions
Needs Improvement (0-13): Unclear writing that impedes comprehension

TOTAL: 100 points

GRADING SCALE:
A: 90-100 points
B: 80-89 points  
C: 70-79 points
D: 60-69 points
F: Below 60 points
        """,
        
        "marking_guide.txt": """
DETAILED MARKING GUIDE

For each criterion, assess the following sub-components:

THESIS AND ARGUMENT CLARITY (20 points)
- Thesis statement clarity (5 points)
- Argument structure (5 points)
- Logical progression (5 points)
- Counterargument consideration (5 points)

EVIDENCE AND SOURCES (25 points)
- Source credibility (8 points)
- Source integration (8 points)
- Citation accuracy (4 points)
- Evidence relevance (5 points)

SCIENTIFIC ACCURACY (20 points)
- Factual correctness (10 points)
- Terminology usage (5 points)
- Conceptual understanding (5 points)

ORGANIZATION AND FLOW (15 points)
- Introduction effectiveness (4 points)
- Body paragraph structure (4 points)
- Conclusion strength (4 points)
- Transition quality (3 points)

WRITING QUALITY (20 points)
- Sentence variety (5 points)
- Word choice (5 points)
- Grammar and mechanics (5 points)
- Overall clarity (5 points)

ADDITIONAL NOTES:
- Deduct 2 points for every day late
- Bonus points (up to 5) for exceptional insight or creativity
- Minimum word count: 800 words (deduct 5 points if under)
        """,
        
        "guidelines.txt": """
ENVIRONMENTAL SCIENCE ESSAY ASSIGNMENT GUIDELINES

ASSIGNMENT OVERVIEW:
Write a 1000-1500 word analytical essay on the impacts of climate change on Arctic wildlife. Your essay should demonstrate understanding of ecological principles and ability to synthesize scientific information.

REQUIREMENTS:
1. Choose a specific focus within Arctic wildlife impacts
2. Use at least 5 credible scientific sources
3. Include proper APA citations and reference list
4. Demonstrate understanding of ecological concepts
5. Present clear arguments supported by evidence

STRUCTURE EXPECTATIONS:
- Introduction with clear thesis statement
- Body paragraphs with topic sentences and supporting evidence
- Logical flow between ideas
- Strong conclusion that synthesizes key points

EVALUATION CRITERIA:
Your essay will be evaluated on argument clarity, use of evidence, scientific accuracy, organization, and writing quality. See the accompanying rubric for detailed point allocations.

SUBMISSION REQUIREMENTS:
- Double-spaced, 12pt Times New Roman font
- 1-inch margins
- Include word count
- Submit as .docx or .pdf file

DUE DATE: [Date to be specified]
LATE PENALTY: -2 points per day late

ACADEMIC INTEGRITY:
All work must be original. Properly cite all sources to avoid plagiarism. Use of AI writing tools is not permitted for this assignment.
        """
    }
    
    # Write support files
    for filename, content in support_files.items():
        with open(support_files_dir / filename, 'w') as f:
            f.write(content.strip())
    
    # Create configuration file
    config = {
        "workflow": "enhanced",
        "provider": "openai",
        "model": "gpt-4-turbo", 
        "temperature": 0.3,
        "system_prompt": "You are an expert environmental science instructor. Grade student essays according to the provided rubric, giving detailed feedback that helps students improve their scientific writing and understanding.",
        "user_prompt": "Please provide:\n1. An overall grade (A, B, C, D, or F) based on the rubric\n2. Points for each rubric criterion with brief justification\n3. Constructive feedback highlighting strengths and areas for improvement\n4. Specific suggestions for enhancing scientific writing and argumentation",
        "rubric_path": str(support_files_dir / "rubric.txt"),
        "marking_guide_path": str(support_files_dir / "marking_guide.txt"),
        "guidelines_path": str(support_files_dir / "guidelines.txt"),
        "document_analysis_url": "http://localhost:8001",
        "max_workers": 2,
        "output_format": "json"
    }
    
    config_path = study_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Example study setup complete in: {study_dir.absolute()}")
    print(f"  - Created {len(sample_essays)} sample submissions")
    print(f"  - Created {len(support_files)} support files")
    print(f"  - Configuration saved to: {config_path}")
    
    return study_dir

def run_example_study(study_dir):
    """Run the example grading study"""
    
    print("\n=== Running Example Study ===")
    
    config_path = study_dir / "config.json"
    submissions_path = study_dir / "submissions"
    results_path = study_dir / "results"
    
    # Run basic workflow
    print("\n1. Running Basic Workflow...")
    basic_cmd = [
        "python", "batch_grader.py", "grade",
        "--directory", str(submissions_path),
        "--config", str(config_path),
        "--workflow", "basic",
        "--output", str(results_path / "basic_results")
    ]
    
    try:
        result = subprocess.run(basic_cmd, capture_output=True, text=True, cwd=".")
        print(f"Basic workflow completed. Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error output: {result.stderr}")
    except Exception as e:
        print(f"Error running basic workflow: {e}")
    
    # Run enhanced workflow  
    print("\n2. Running Enhanced Workflow...")
    enhanced_cmd = [
        "python", "batch_grader.py", "grade", 
        "--directory", str(submissions_path),
        "--config", str(config_path),
        "--workflow", "enhanced",
        "--output", str(results_path / "enhanced_results")
    ]
    
    try:
        result = subprocess.run(enhanced_cmd, capture_output=True, text=True, cwd=".")
        print(f"Enhanced workflow completed. Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error output: {result.stderr}")
    except Exception as e:
        print(f"Error running enhanced workflow: {e}")
    
    # Run comparison
    print("\n3. Running Workflow Comparison...")
    compare_cmd = [
        "python", "batch_grader.py", "compare",
        "--directory", str(submissions_path),
        "--workflows", "basic,enhanced", 
        "--output", str(results_path / "comparison")
    ]
    
    try:
        result = subprocess.run(compare_cmd, capture_output=True, text=True, cwd=".")
        print(f"Comparison completed. Return code: {result.returncode}")
        if result.returncode != 0:
            print(f"Error output: {result.stderr}")
    except Exception as e:
        print(f"Error running comparison: {e}")
    
    print(f"\n✓ Study complete! Results saved in: {results_path}")

if __name__ == "__main__":
    print("AI Assessor CLI - Example Research Study")
    print("=" * 40)
    
    # Setup the example study
    study_dir = setup_example_study()
    
    # Ask user if they want to run the study
    response = input(f"\nRun the example study? (y/n): ").lower().strip()
    
    if response == 'y':
        run_example_study(study_dir)
        print("\nExample study completed!")
        print("\nTo analyze results, check the files in:")
        print(f"  {study_dir / 'results'}")
        print("\nExample commands to explore results:")
        print("  cat example_study/results/basic_results.json")
        print("  cat example_study/results/enhanced_results.json")
        print("  cat example_study/results/comparison_comparison.json")
    else:
        print(f"\nStudy setup is ready in: {study_dir}")
        print("You can run the batch grader manually using:")
        print(f"  python batch_grader.py grade --directory {study_dir}/submissions --config {study_dir}/config.json")