import configparser
import os
from ..utils.error_handling import ErrorHandler

class ConfigManager:
    """
    Manages configuration settings for the application.
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
                ErrorHandler.handle_file_error(e, self.config_file)
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
        except Exception as e:
            ErrorHandler.handle_validation_error(e, f"{section}.{option}")
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
        except Exception as e:
            ErrorHandler.handle_validation_error(e, f"{section}.{option}")
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
            ErrorHandler.handle_file_error(e, self.config_file)
            return False
    
    def get_model_name(self, model_key):
        """
        Get the actual model name from the model key.
        
        Args:
            model_key (str): Model key (e.g., "GPT-3", "GPT-4")
            
        Returns:
            str: Actual model name for the API
        """
        return self.get_value("Models", model_key, model_key)