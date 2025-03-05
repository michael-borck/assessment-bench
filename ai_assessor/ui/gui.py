import os
import tkinter as tk
from tkinter import ttk, messagebox

from .views.config_view import ConfigView
from .views.grading_view import GradingView

class AIAssessorGUI:
    """
    Main GUI class for the AI Assessor application.
    """
    
    def __init__(self, root, assessor, config_manager):
        """
        Initialize the GUI.
        
        Args:
            root (tk.Tk): The root Tkinter window
            assessor (Assessor): The assessor instance
            config_manager (ConfigManager): The configuration manager
        """
        self.root = root
        self.assessor = assessor
        self.config_manager = config_manager
        
        # Set window size
        self.root.geometry("1000x800")
        
        # Create StringVar variables for configuration paths
        self.string_vars = {
            "api_key": tk.StringVar(value=self.config_manager.get_value("API", "Key", "")),
            "system_prompt_path": tk.StringVar(value=self.config_manager.get_value("Paths", "SystemPromptPath", "")),
            "user_prompt_path": tk.StringVar(value=self.config_manager.get_value("Paths", "UserPromptPath", "")),
            "support_folder": tk.StringVar(value=self.config_manager.get_value("Paths", "SupportFolder", "")),
            "submissions_folder": tk.StringVar(value=self.config_manager.get_value("Paths", "SubmissionsFolder", "")),
            "output_folder": tk.StringVar(value=self.config_manager.get_value("Paths", "OutputFolder", "")),
            "model": tk.StringVar(value=self.config_manager.get_value("API", "DefaultModel", "GPT-4")),
            "temperature": tk.StringVar(value=self.config_manager.get_value("API", "Temperature", "0.7"))
        }
        
        # Setup UI
        self.setup_ui()
        
        # Register callback to save configuration on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Set up the main UI elements."""
        # Create notebook (tabbed interface)
        self.tab_control = ttk.Notebook(self.root)
        
        # Create tabs
        self.config_tab = ConfigView(self.tab_control, self.config_manager, self.string_vars)
        self.tab_control.add(self.config_tab, text="Configuration and Prompts")
        
        self.grading_tab = GradingView(self.tab_control, self.assessor, self.config_manager, self.string_vars)
        self.tab_control.add(self.grading_tab, text="Grading")
        
        # Register tab change event
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        
        # Pack the notebook to fill the window
        self.tab_control.pack(expand=1, fill="both")
    
    def on_tab_selected(self, event):
        """
        Handle tab selection events.
        
        Args:
            event: The tab selection event
        """
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # Update file list when switching to grading tab
        if tab_text == "Grading":
            self.grading_tab.update_file_list()
    
    def on_closing(self):
        """Handle window close event and save configuration."""
        # Save configuration values from StringVars
        self.config_manager.set_value("API", "Key", self.string_vars["api_key"].get())
        self.config_manager.set_value("Paths", "SystemPromptPath", self.string_vars["system_prompt_path"].get())
        self.config_manager.set_value("Paths", "UserPromptPath", self.string_vars["user_prompt_path"].get())
        self.config_manager.set_value("Paths", "SupportFolder", self.string_vars["support_folder"].get())
        self.config_manager.set_value("Paths", "SubmissionsFolder", self.string_vars["submissions_folder"].get())
        self.config_manager.set_value("Paths", "OutputFolder", self.string_vars["output_folder"].get())
        self.config_manager.set_value("API", "DefaultModel", self.string_vars["model"].get())
        self.config_manager.set_value("API", "Temperature", self.string_vars["temperature"].get())
        
        # Save configuration
        self.config_manager.save()
        
        # Close the window
        self.root.destroy()