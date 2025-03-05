#!/usr/bin/env python3
"""
AI Assessor - An AI-powered tool for grading student submissions.
"""

import os
import tkinter as tk
from dotenv import load_dotenv

# Import core components
from aiassessor.core import OpenAIClient, Assessor
from aiassessor.config import ConfigManager
from aiassessor.utils import ErrorHandler

# Set up logging
ErrorHandler.setup_logging()

def main():
    """
    Main entry point for the application.
    """
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
    
    # Start GUI
    # For now, we'll import the GUI here to avoid circular imports
    # In future, we can add CLI or web interface conditionally
    from aiassessor.ui.gui import AIAssessorGUI
    
    # Initialize and run the GUI
    root = tk.Tk()
    root.title("AI Assessor")
    app = AIAssessorGUI(root, assessor, config_manager)
    root.mainloop()

if __name__ == "__main__":
    main()