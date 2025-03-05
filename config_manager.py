import configparser
import os

def read_config(config_file):
    """
    Reads configuration settings from a config file.
    """
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        print(f"Configuration file {config_file} not found.")
        return None

    config.read(config_file)
    return config

def write_config(config_file, section, key, value):
    """
    Writes a configuration setting to a config file.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    if section not in config:
        config.add_section(section)

    config.set(section, key, value)

    with open(config_file, 'w') as file:
        config.write(file)

def get_config_value(config, section, key):
    """
    Retrieves a specific configuration value.
    """
    try:
        return config[section][key]
    except KeyError:
        print(f"Key '{key}' not found in section '{section}'.")
        return None

# Example usage
# config = read_config('path/to/config.ini')
# api_key = get_config_value(config, 'API', 'OPENAI_API_KEY')

