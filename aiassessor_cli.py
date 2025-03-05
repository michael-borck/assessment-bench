#!/usr/bin/env python3
"""
AI Assessor CLI - Command-line interface for AI Assessor.
"""

import os
import sys
from dotenv import load_dotenv

# Import core components
from aiassessor.core import OpenAIClient, Assessor
from aiassessor.config import ConfigManager
from aiassessor.cli import AIAssessorCLI
from aiassessor.utils import ErrorHandler

def main():
    """
    Main entry point for the CLI application.
    """
    # Set up logging
    ErrorHandler.setup_logging()
    
    # Load environment variables for API key
    load_dotenv()
    
    # Initialize configuration
    config_manager = ConfigManager("config.ini")
    
    # Get API key from environment or config
    api_key = os.getenv("OPENAI_API_KEY") or config_manager.get_value("API", "Key", "")
    
    # Initialize API client
    api_client = OpenAIClient(api_key)
    
    # Initialize assessor
    assessor = Assessor(api_client, config_manager)
    
    # Initialize and run the CLI
    cli = AIAssessorCLI(assessor, config_manager)
    exit_code = cli.run(sys.argv[1:])
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()