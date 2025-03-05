#!/usr/bin/env python3
"""
Standalone version of AI Assessor for PyInstaller packaging.
"""

import os
import sys
import tkinter as tk
from dotenv import load_dotenv
import configparser
import logging

# Add the current directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Try to import from relative paths first (for PyInstaller)
try:
    from core.api_client import OpenAIClient
    from core.assessor import Assessor
except ImportError:
    # Fall back to package imports
    from aiassessor.core import OpenAIClient, Assessor

# Define ConfigManager here for PyInstaller
class ConfigManager:
    """
    Simplified ConfigManager for standalone distribution.
    """
    
    DEFAULT_CONFIG = {
        "Paths": {
            "SystemPromptPath": "",
            "UserPromptPath": "",
            "SupportFolder": "",
            "SubmissionsFolder": "",
            "OutputFolder": ""
        },
        "API": {
            "Key": "",
            "DefaultModel": "gpt-4-turbo",
            "Temperature": "0.7"
        },
        "Models": {
            "gpt-3.5-turbo": "gpt-3.5-turbo",
            "gpt-4-turbo": "gpt-4-turbo",
            "gpt-4o": "gpt-4o"
        }
    }
    
    def __init__(self, config_file="config.ini"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str): Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """
        Load configuration from file or create with defaults.
        
        Returns:
            ConfigParser: Loaded configuration
        """
        config = configparser.ConfigParser()
        
        # Try to load existing config
        if os.path.exists(self.config_file):
            try:
                config.read(self.config_file)
            except Exception as e:
                print(f"Error loading config: {e}")
                # Fall back to defaults if loading fails
                self._set_defaults(config)
        else:
            # Create new config with defaults
            self._set_defaults(config)
            self.save()
            
        return config
    
    def _set_defaults(self, config):
        """
        Set default values for configuration.
        
        Args:
            config (ConfigParser): Configuration to set defaults on
        """
        for section, options in self.DEFAULT_CONFIG.items():
            if not config.has_section(section):
                config.add_section(section)
                
            for option, value in options.items():
                if not config.has_option(section, option):
                    config.set(section, option, value)
    
    def get_value(self, section, option, default=None):
        """
        Get a configuration value.
        
        Args:
            section (str): Configuration section
            option (str): Configuration option
            default (str, optional): Default value if not found
            
        Returns:
            str: Configuration value or default
        """
        try:
            if self.config.has_option(section, option):
                return self.config.get(section, option)
            return default
        except Exception:
            return default
    
    def set_value(self, section, option, value):
        """
        Set a configuration value.
        
        Args:
            section (str): Configuration section
            option (str): Configuration option
            value (str): Value to set
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
                
            self.config.set(section, option, str(value))
            return True
        except Exception:
            return False
    
    def save(self):
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful
        """
        try:
            directory = os.path.dirname(self.config_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_model_name(self, model_key):
        """
        Get the actual model name from the model key.
        
        Args:
            model_key (str): Model key
            
        Returns:
            str: Actual model name for the API
        """
        return self.get_value("Models", model_key, model_key)

# Import GUI components
try:
    from aiassessor.ui.gui import AIAssessorGUI
except ImportError:
    # Load GUI dynamically for PyInstaller
    import importlib.util
    
    # First, try to load from current directory
    gui_path = os.path.join(os.path.dirname(__file__), "aiassessor", "ui", "gui.py")
    if not os.path.exists(gui_path):
        # Look in the same directory
        gui_path = os.path.join(os.path.dirname(__file__), "gui.py")
    
    if os.path.exists(gui_path):
        spec = importlib.util.spec_from_file_location("gui", gui_path)
        gui_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gui_module)
        AIAssessorGUI = gui_module.AIAssessorGUI
    else:
        raise ImportError("Could not find GUI module")

def setup_logging():
    """Set up basic logging."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "aiassessor.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    """
    Main entry point for the standalone application.
    """
    # Set up logging
    setup_logging()
    
    # Load environment variables for API key
    load_dotenv()
    
    # Get the base directory (works in PyInstaller bundle too)
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set config file path
    config_file = os.path.join(base_dir, "config.ini")
    
    # Initialize configuration
    config_manager = ConfigManager(config_file)
    
    # Get API key from environment or config
    api_key = os.getenv("OPENAI_API_KEY") or config_manager.get_value("API", "Key", "")
    
    # Initialize API client
    api_client = OpenAIClient(api_key)
    
    # Initialize assessor
    assessor = Assessor(api_client, config_manager)
    
    # Initialize and run the GUI
    root = tk.Tk()
    root.title("AI Assessor")
    app = AIAssessorGUI(root, assessor, config_manager)
    root.mainloop()

if __name__ == "__main__":
    main()