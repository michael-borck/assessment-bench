import os
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import threading
import time
from openai import OpenAI

from .views.config_view import ConfigView
from .views.grading_view import GradingView

class SplashScreen:
    """
    Splash screen to display while the application loads.
    """
    def __init__(self, root):
        self.root = root
        self.splash_root = tk.Toplevel(root)
        self.splash_root.title("Loading...")
        
        # Remove window decorations
        self.splash_root.overrideredirect(True)
        
        # Calculate position for center of screen
        screen_width = self.splash_root.winfo_screenwidth()
        screen_height = self.splash_root.winfo_screenheight()
        width = 500
        height = 300
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.splash_root.geometry(f"{width}x{height}+{x}+{y}")
        self.splash_root.configure(background="#f0f0f0")
        
        # Try to load logo if available
        try:
            self.logo = tk.PhotoImage(file="ai_assessor/ui/assets/logo.png")
            logo_label = tk.Label(self.splash_root, image=self.logo, background="#f0f0f0")
            logo_label.pack(pady=20)
        except Exception:
            # If logo not found, just display text
            title_label = tk.Label(self.splash_root, text="AI Assessor", 
                                 font=("Helvetica", 24, "bold"),
                                 background="#f0f0f0")
            title_label.pack(pady=20)
        
        # Application title and version
        app_label = tk.Label(self.splash_root, text="AI Assessor", 
                           font=("Helvetica", 18),
                           background="#f0f0f0")
        app_label.pack()
        
        version_label = tk.Label(self.splash_root, text="Version 1.0", 
                               font=("Helvetica", 10),
                               background="#f0f0f0")
        version_label.pack()
        
        # Loading bar
        self.progress = ttk.Progressbar(self.splash_root, orient="horizontal",
                                      length=400, mode="determinate")
        self.progress.pack(pady=20)
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        status_label = tk.Label(self.splash_root, textvariable=self.status_var,
                              font=("Helvetica", 10),
                              background="#f0f0f0")
        status_label.pack(pady=10)
        
    def update_progress(self, value, status=""):
        """Update the progress bar and status message."""
        self.progress["value"] = value
        if status:
            self.status_var.set(status)
        self.splash_root.update_idletasks()
        
    def destroy(self):
        """Close the splash screen."""
        self.splash_root.destroy()


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
        
        # Hide main window during splash
        root.withdraw()
        
        # Create splash screen
        self.splash = SplashScreen(root)
        
        # Start loading process
        threading.Thread(target=self.initialize_app).start()
    
    def initialize_app(self):
        """Initialize the application in the background."""
        # Start initialization process
        self.splash.update_progress(10, "Loading configuration...")
        time.sleep(0.5)  # Simulate loading
        
        # Set window size
        self.root.geometry("1000x800")
        self.root.title("AI Assessor")
        
        try:
            # Try to load logo if available
            self.root.iconphoto(False, PhotoImage(file="ai_assessor/ui/assets/icon.png"))
        except Exception:
            pass
        
        # Create StringVar variables for configuration paths
        self.splash.update_progress(30, "Initializing variables...")
        time.sleep(0.3)  # Simulate loading
        
        self.string_vars = {
            "api_key": tk.StringVar(value=self.config_manager.get_value("API", "Key", "")),
            "system_prompt_path": tk.StringVar(value=self.config_manager.get_value("Paths", "SystemPromptPath", "")),
            "user_prompt_path": tk.StringVar(value=self.config_manager.get_value("Paths", "UserPromptPath", "")),
            "support_folder": tk.StringVar(value=self.config_manager.get_value("Paths", "SupportFolder", "")),
            "submissions_folder": tk.StringVar(value=self.config_manager.get_value("Paths", "SubmissionsFolder", "")),
            "output_folder": tk.StringVar(value=self.config_manager.get_value("Paths", "OutputFolder", "")),
            "model": tk.StringVar(value=self.config_manager.get_value("API", "DefaultModel", "gpt-4-turbo")),
            "temperature": tk.StringVar(value=self.config_manager.get_value("API", "Temperature", "0.7"))
        }
        
        # Fetch available models if API key exists
        self.splash.update_progress(50, "Checking for available models...")
        self.available_models = []
        api_key = self.string_vars["api_key"].get()
        if api_key:
            try:
                self.fetch_available_models(api_key)
            except Exception:
                # If fetching fails, use default models
                pass
        
        # Setup UI
        self.splash.update_progress(70, "Building user interface...")
        time.sleep(0.5)  # Simulate loading
        self.setup_ui()
        
        # Register callback to save configuration on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Finalize loading
        self.splash.update_progress(100, "Ready!")
        time.sleep(0.5)  # Show 100% for a moment
        
        # Show main window and destroy splash
        self.root.deiconify()
        self.splash.destroy()
        
        # Check if API key is set, if not, show settings dialog
        if not api_key:
            self.show_first_run_dialog()
    
    def fetch_available_models(self, api_key):
        """Fetch available models from OpenAI API."""
        try:
            # Try with a timeout to avoid hanging
            import httpx
            client = OpenAI(
                api_key=api_key,
                timeout=httpx.Timeout(10.0)  # 10 second timeout
            )
            models = client.models.list()
            
            # Filter for chat models
            chat_models = [model.id for model in models.data 
                         if model.id.startswith(('gpt-3.5', 'gpt-4'))]
            
            # Sort models: put gpt-4 first, then gpt-3.5
            gpt4_models = sorted([m for m in chat_models if m.startswith('gpt-4')])
            gpt35_models = sorted([m for m in chat_models if m.startswith('gpt-3.5')])
            
            self.available_models = gpt4_models + gpt35_models
            
            # Log success for debugging
            print(f"Successfully fetched {len(self.available_models)} models")
        except Exception as e:
            # If fetching fails, use default models
            print(f"Error fetching models: {str(e)}")
            self.available_models = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
    
    def setup_ui(self):
        """Set up the main UI elements."""
        # Create menu bar
        self.create_menu()
        
        # Apply modern styling
        self.apply_styles()
        
        # Create notebook (tabbed interface)
        self.tab_control = ttk.Notebook(self.root)
        
        # Create grading tab first (now the default view)
        self.grading_tab = GradingView(self.tab_control, self.assessor, self.config_manager, self.string_vars)
        self.tab_control.add(self.grading_tab, text="Grade Submissions")
        
        # Create config tab
        self.config_tab = ConfigView(self.tab_control, self.config_manager, self.string_vars, self.available_models)
        self.tab_control.add(self.config_tab, text="Settings")
        
        # Register tab change event
        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        
        # Pack the notebook to fill the window
        self.tab_control.pack(expand=1, fill="both")
        
        # Create status bar
        self.create_status_bar()
    
    def create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Settings", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Grade menu
        grade_menu = tk.Menu(menubar, tearoff=0)
        grade_menu.add_command(label="Grade Selected", command=self.grade_selected)
        grade_menu.add_command(label="Grade All", command=self.grade_all)
        menubar.add_cascade(label="Grade", menu=grade_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="View Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_status_bar(self):
        """Create status bar at the bottom of the window."""
        status_frame = ttk.Frame(self.root, relief="sunken", padding=(2, 2))
        status_frame.pack(side="bottom", fill="x")
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, anchor="w")
        status_label.pack(side="left", padx=5)
        
        # API status indicator
        api_frame = ttk.Frame(status_frame)
        api_frame.pack(side="right", padx=5)
        
        ttk.Label(api_frame, text="API:").pack(side="left")
        
        self.api_status_var = tk.StringVar()
        self.api_status_var.set("Not configured" if not self.string_vars["api_key"].get() else "Ready")
        
        self.api_status_color = "red" if not self.string_vars["api_key"].get() else "green"
        self.api_status = ttk.Label(api_frame, textvariable=self.api_status_var, 
                                 foreground=self.api_status_color)
        self.api_status.pack(side="left", padx=5)
        
        # Model indicator
        model_frame = ttk.Frame(status_frame)
        model_frame.pack(side="right", padx=10)
        
        ttk.Label(model_frame, text="Model:").pack(side="left")
        
        model_label = ttk.Label(model_frame, textvariable=self.string_vars["model"])
        model_label.pack(side="left", padx=5)
    
    def apply_styles(self):
        """Apply modern styling to the application."""
        style = ttk.Style()
        
        # Use a more modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        
        # Configure styles
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TEntry', font=('Helvetica', 10))
        style.configure('TNotebook', font=('Helvetica', 10))
        style.configure('TNotebook.Tab', font=('Helvetica', 10))
    
    def update_status(self, message):
        """Update status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def update_api_status(self):
        """Update API status indicator."""
        if self.string_vars["api_key"].get():
            self.api_status_var.set("Ready")
            self.api_status.configure(foreground="green")
        else:
            self.api_status_var.set("Not configured")
            self.api_status.configure(foreground="red")
    
    def on_tab_selected(self, event):
        """
        Handle tab selection events.
        
        Args:
            event: The tab selection event
        """
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # Update file list when switching to grading tab
        if tab_text == "Grade Submissions":
            self.grading_tab.update_file_list()
            self.update_status("Ready to grade submissions")
        elif tab_text == "Settings":
            self.update_status("Configure application settings")
    
    def show_settings(self):
        """Switch to settings tab."""
        self.tab_control.select(1)  # Select the settings tab
    
    def grade_selected(self):
        """Grade selected submission from menu."""
        self.tab_control.select(0)  # Select the grading tab
        self.grading_tab.grade_selected()
    
    def grade_all(self):
        """Grade all submissions from menu."""
        self.tab_control.select(0)  # Select the grading tab
        self.grading_tab.grade_all()
    
    def show_documentation(self):
        """Show documentation in a new window."""
        doc_window = tk.Toplevel(self.root)
        doc_window.title("AI Assessor Documentation")
        doc_window.geometry("600x500")
        doc_window.transient(self.root)
        
        # Documentation content
        content_frame = ttk.Frame(doc_window, padding=20)
        content_frame.pack(fill="both", expand=True)
        
        ttk.Label(content_frame, text="AI Assessor Documentation", 
                font=("Helvetica", 16, "bold")).pack(pady=(0, 20))
        
        # Scrollable text area for documentation
        text_frame = ttk.Frame(content_frame)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_area = tk.Text(text_frame, wrap="word", yscrollcommand=scrollbar.set)
        text_area.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_area.yview)
        
        # Documentation text
        doc_text = """
AI Assessor User Guide

Overview:
---------
AI Assessor is a tool for automatically grading student submissions using OpenAI's language models. The application reads Word documents, processes them against a rubric or grading criteria, and generates feedback.

Getting Started:
---------------
1. API Key: You need an OpenAI API key to use this application. Enter it in the Settings tab.

2. Folders Setup:
   - Prompts: Contains system and user prompts that guide the AI
   - Submissions: Place student documents (.docx) here
   - Support: Contains rubrics and grading guidelines
   - Output: Where graded assessments will be saved

3. Grading:
   - Select a file from the submissions list
   - Click "Grade Selected" to process a single submission
   - Click "Grade All" to process all submissions in the folder

4. Customization:
   - Edit prompts to customize grading style and focus
   - Choose different models for different complexity levels
   - Adjust temperature to control AI creativity/randomness

Tips:
-----
- Higher temperature (closer to 1.0) gives more varied responses
- GPT-4 models provide more detailed feedback but cost more
- Save common prompt templates for reuse

Support:
--------
For issues or feature requests, please contact your system administrator.
        """
        
        text_area.insert("1.0", doc_text)
        text_area.config(state="disabled")  # Make read-only
        
        # Close button
        ttk.Button(content_frame, text="Close", command=doc_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
AI Assessor

Version 1.0

A tool for automatically grading student submissions using OpenAI's language models.

© 2023-2025 All Rights Reserved
        """
        messagebox.showinfo("About AI Assessor", about_text)
    
    def show_first_run_dialog(self):
        """Show first-run dialog if API key not configured."""
        if not self.string_vars["api_key"].get():
            response = messagebox.askyesno(
                "Welcome to AI Assessor",
                "It looks like this is your first time running AI Assessor. "
                "Would you like to configure your OpenAI API key now?"
            )
            if response:
                self.show_settings()
    
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