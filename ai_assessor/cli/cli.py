import os
import sys
import argparse
import logging
from tqdm import tqdm

from ..core import Assessor
from ..utils import DocumentProcessor, FileUtils, ErrorHandler
from ..config import ConfigManager

class AIAssessorCLI:
    """
    Command-line interface for AI Assessor.
    """
    
    def __init__(self, assessor, config_manager):
        """
        Initialize the CLI.
        
        Args:
            assessor (Assessor): The assessor instance
            config_manager (ConfigManager): The configuration manager
        """
        self.assessor = assessor
        self.config_manager = config_manager
        self.doc_processor = DocumentProcessor()
    
    def setup_parser(self):
        """
        Set up command-line argument parser.
        
        Returns:
            ArgumentParser: The argument parser
        """
        parser = argparse.ArgumentParser(
            description="AI Assessor - An AI-powered tool for grading student submissions.",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Add subparsers for different commands
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # Config command
        config_parser = subparsers.add_parser("config", help="Configure the application")
        config_parser.add_argument("--list", action="store_true", help="List all configuration settings")
        config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration value (e.g., API.Key value)")
        config_parser.add_argument("--get", metavar="KEY", help="Get a configuration value (e.g., API.Key)")
        
        # Grade command
        grade_parser = subparsers.add_parser("grade", help="Grade submissions")
        grade_parser.add_argument("--file", help="Path to a single submission file to grade")
        grade_parser.add_argument("--dir", help="Path to a directory of submission files to grade")
        grade_parser.add_argument("--system", help="Path to the system prompt file")
        grade_parser.add_argument("--user", help="Path to the user prompt file")
        grade_parser.add_argument("--support", help="Path to the directory containing support files")
        grade_parser.add_argument("--output", help="Path to the output directory for feedback files")
        grade_parser.add_argument("--model", choices=["GPT-3", "GPT-4"], help="Model to use for grading")
        grade_parser.add_argument("--temp", type=float, help="Temperature setting (0-1) for the model")
        
        # Interactive command
        interactive_parser = subparsers.add_parser("interactive", help="Enter interactive mode")
        
        return parser
    
    def run(self, args=None):
        """
        Run the CLI with the given arguments.
        
        Args:
            args (list, optional): Command-line arguments
        
        Returns:
            int: Exit code
        """
        parser = self.setup_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return 0
        
        if parsed_args.command == "config":
            return self.handle_config_command(parsed_args)
        elif parsed_args.command == "grade":
            return self.handle_grade_command(parsed_args)
        elif parsed_args.command == "interactive":
            return self.start_interactive_mode()
        else:
            parser.print_help()
            return 1
    
    def handle_config_command(self, args):
        """
        Handle the config command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            int: Exit code
        """
        if args.list:
            # List all configuration settings
            self.list_config()
        elif args.set:
            # Set a configuration value
            key, value = args.set
            if "." in key:
                section, option = key.split(".", 1)
                self.config_manager.set_value(section, option, value)
                self.config_manager.save()
                print(f"Set {key} to {value}")
            else:
                print(f"Error: Key should be in the format 'Section.Option'")
                return 1
        elif args.get:
            # Get a configuration value
            key = args.get
            if "." in key:
                section, option = key.split(".", 1)
                value = self.config_manager.get_value(section, option)
                print(f"{key} = {value}")
            else:
                print(f"Error: Key should be in the format 'Section.Option'")
                return 1
        else:
            # Show config help
            print("Use --list to show all settings, --set to change a setting, or --get to view a setting.")
            return 1
        
        return 0
    
    def list_config(self):
        """List all configuration settings."""
        print("AI Assessor Configuration:")
        print("--------------------------")
        
        for section in self.config_manager.config.sections():
            print(f"[{section}]")
            for option in self.config_manager.config.options(section):
                value = self.config_manager.get_value(section, option)
                print(f"  {option} = {value}")
            print()
    
    def handle_grade_command(self, args):
        """
        Handle the grade command.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            int: Exit code
        """
        # Use provided values or defaults from config
        system_prompt_path = args.system or self.config_manager.get_value("Paths", "SystemPromptPath")
        user_prompt_path = args.user or self.config_manager.get_value("Paths", "UserPromptPath")
        support_folder = args.support or self.config_manager.get_value("Paths", "SupportFolder")
        output_folder = args.output or self.config_manager.get_value("Paths", "OutputFolder")
        model = args.model or self.config_manager.get_value("API", "DefaultModel", "GPT-4")
        
        # Parse temperature
        try:
            if args.temp is not None:
                temperature = args.temp
                if temperature < 0 or temperature > 1:
                    raise ValueError("Temperature must be between 0 and 1")
            else:
                temp_str = self.config_manager.get_value("API", "Temperature", "0.7")
                temperature = float(temp_str)
        except ValueError as e:
            print(f"Error: Invalid temperature value: {e}")
            return 1
        
        # Validate required paths
        if not system_prompt_path or not os.path.exists(system_prompt_path):
            print("Error: System prompt file not found. Use --system or set Paths.SystemPromptPath in config.")
            return 1
        
        if not user_prompt_path or not os.path.exists(user_prompt_path):
            print("Error: User prompt file not found. Use --user or set Paths.UserPromptPath in config.")
            return 1
        
        # Read prompt content
        try:
            system_prompt = self.doc_processor.read_text_file(system_prompt_path)
            user_prompt = self.doc_processor.read_text_file(user_prompt_path)
        except Exception as e:
            print(f"Error reading prompts: {e}")
            return 1
        
        # Create output directory if it doesn't exist
        if output_folder:
            try:
                FileUtils.ensure_dir_exists(output_folder)
            except Exception as e:
                print(f"Error creating output directory: {e}")
                return 1
        
        # Grade submissions
        if args.file:
            # Grade a single file
            if not os.path.exists(args.file):
                print(f"Error: Submission file not found: {args.file}")
                return 1
            
            print(f"Grading submission: {os.path.basename(args.file)}")
            print(f"Using model: {model}, temperature: {temperature}")
            
            try:
                success, feedback = self.assessor.grade_submission(
                    submission_file=args.file,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    support_files=support_folder,
                    output_folder=output_folder,
                    model=model,
                    temperature=temperature
                )
                
                if success:
                    print("✓ Grading successful")
                    if output_folder:
                        feedback_filename = os.path.basename(args.file).replace(".docx", "_feedback.txt")
                        print(f"  Feedback saved to: {os.path.join(output_folder, feedback_filename)}")
                else:
                    print(f"✗ Grading failed: {feedback}")
                    return 1
            except Exception as e:
                print(f"Error grading submission: {e}")
                return 1
            
        elif args.dir:
            # Grade all files in a directory
            if not os.path.exists(args.dir) or not os.path.isdir(args.dir):
                print(f"Error: Submissions directory not found: {args.dir}")
                return 1
            
            try:
                # Get all docx files
                docx_files = FileUtils.get_docx_files(args.dir)
                
                if not docx_files:
                    print("No submission files (*.docx) found in the directory.")
                    return 1
                
                print(f"Found {len(docx_files)} submission files")
                print(f"Using model: {model}, temperature: {temperature}")
                
                # Grade all submissions with progress bar
                success_count = 0
                fail_count = 0
                
                for filename in tqdm(docx_files, desc="Grading submissions"):
                    submission_path = os.path.join(args.dir, filename)
                    
                    try:
                        success, feedback = self.assessor.grade_submission(
                            submission_file=submission_path,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            support_files=support_folder,
                            output_folder=output_folder,
                            model=model,
                            temperature=temperature
                        )
                        
                        if success:
                            success_count += 1
                        else:
                            fail_count += 1
                            print(f"✗ Failed to grade {filename}: {feedback}")
                    except Exception as e:
                        fail_count += 1
                        print(f"✗ Error grading {filename}: {e}")
                
                print(f"Grading completed: {success_count} succeeded, {fail_count} failed")
                
                if fail_count > 0:
                    return 1
                
            except Exception as e:
                print(f"Error processing submissions: {e}")
                return 1
            
        else:
            print("Error: Please specify either --file or --dir")
            return 1
        
        return 0
    
    def start_interactive_mode(self):
        """
        Start interactive CLI mode.
        
        Returns:
            int: Exit code
        """
        print("AI Assessor Interactive Mode")
        print("---------------------------")
        print("Type 'help' for available commands, 'exit' to quit.")
        
        while True:
            try:
                command = input("\naiassessor> ").strip()
                
                if command.lower() in ["exit", "quit", "q"]:
                    break
                
                if command.lower() in ["help", "?"]:
                    self.print_interactive_help()
                    continue
                
                # Process command
                args = command.split()
                if args:
                    self.run(args)
                
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Exiting interactive mode.")
        return 0
    
    def print_interactive_help(self):
        """Print help for interactive mode."""
        print("Available commands:")
        print("  config --list             List all configuration settings")
        print("  config --set KEY VALUE    Set a configuration value")
        print("  config --get KEY          Get a configuration value")
        print("  grade --file FILE         Grade a single submission file")
        print("  grade --dir DIRECTORY     Grade all submissions in a directory")
        print("  help                      Show this help message")
        print("  exit                      Exit interactive mode")
        print()
        print("Examples:")
        print("  config --set API.Key your_api_key")
        print("  grade --file submission.docx --model GPT-4")