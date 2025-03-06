import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

from ...utils.document_processor import DocumentProcessor

class ConfigView(ttk.Frame):
    """
    Configuration tab of the application.
    """
    
    def __init__(self, parent, config_manager, string_vars, available_models=None):
        """
        Initialize the configuration view.
        
        Args:
            parent: The parent widget
            config_manager: The configuration manager
            string_vars: Dictionary of StringVar objects for configuration
            available_models: List of available OpenAI models (optional)
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.string_vars = string_vars
        self.document_processor = DocumentProcessor()
        self.available_models = available_models or []
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements for the configuration tab."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        
        # API Configuration
        row = 0
        ttk.Label(self, text="OpenAI API Key:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.string_vars["api_key"]).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        # Path Configuration
        row += 1
        ttk.Label(self, text="System Prompt Path:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        path_frame = ttk.Frame(self)
        path_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.string_vars["system_prompt_path"]).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=lambda: self.browse_file("System Prompt", self.string_vars["system_prompt_path"])).pack(side="right")
        
        row += 1
        ttk.Label(self, text="User Prompt Path:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        path_frame = ttk.Frame(self)
        path_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.string_vars["user_prompt_path"]).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=lambda: self.browse_file("User Prompt", self.string_vars["user_prompt_path"])).pack(side="right")
        
        row += 1
        ttk.Label(self, text="Support Files Folder:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        path_frame = ttk.Frame(self)
        path_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.string_vars["support_folder"]).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=lambda: self.browse_directory("Support Files", self.string_vars["support_folder"])).pack(side="right")
        
        row += 1
        ttk.Label(self, text="Submissions Folder:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        path_frame = ttk.Frame(self)
        path_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.string_vars["submissions_folder"]).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=lambda: self.browse_directory("Submissions", self.string_vars["submissions_folder"])).pack(side="right")
        
        row += 1
        ttk.Label(self, text="Output Folder:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        path_frame = ttk.Frame(self)
        path_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        ttk.Entry(path_frame, textvariable=self.string_vars["output_folder"]).pack(side="left", fill="x", expand=True)
        ttk.Button(path_frame, text="Browse", command=lambda: self.browse_directory("Output", self.string_vars["output_folder"])).pack(side="right")
        
        # Model Selection
        row += 1
        ttk.Label(self, text="Model:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        model_frame = ttk.Frame(self)
        model_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        # Use available models if fetched, otherwise use config
        if self.available_models:
            model_options = self.available_models
        else:
            model_options = list(self.config_manager.config["Models"].keys()) if self.config_manager.config.has_section("Models") else ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o"]
        
        # Create combobox for model selection
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.string_vars["model"], values=model_options)
        
        # Add button to refresh models
        ttk.Button(model_frame, text="Refresh Models", command=self.refresh_models).pack(side="right", padx=5)
        self.model_dropdown.pack(side="left", fill="x", expand=True)
        
        # Add button to add new model
        ttk.Button(model_frame, text="Manage Models", command=self.manage_models).pack(side="right", padx=5)
        
        # Temperature Setting
        row += 1
        ttk.Label(self, text="Temperature (0-1):").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self, textvariable=self.string_vars["temperature"]).grid(row=row, column=1, sticky="w", padx=5, pady=5, ipadx=10)
        
        # System Prompt Editor
        row += 1
        ttk.Label(self, text="System Prompt:").grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        row += 1
        self.system_prompt_editor = scrolledtext.ScrolledText(self, height=10)
        self.system_prompt_editor.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Buttons for system prompt
        row += 1
        button_frame = ttk.Frame(self)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(button_frame, text="Load System Prompt", command=self.load_system_prompt).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save System Prompt", command=self.save_system_prompt).pack(side="left", padx=5)
        
        # User Prompt Editor
        row += 1
        ttk.Label(self, text="User Prompt:").grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        row += 1
        self.user_prompt_editor = scrolledtext.ScrolledText(self, height=10)
        self.user_prompt_editor.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Buttons for user prompt
        row += 1
        button_frame = ttk.Frame(self)
        button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        ttk.Button(button_frame, text="Load User Prompt", command=self.load_user_prompt).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save User Prompt", command=self.save_user_prompt).pack(side="left", padx=5)
        
        # Load prompts if paths are set
        self.load_initial_prompts()
    
    def browse_file(self, file_type, string_var):
        """
        Browse for a file and update the corresponding path.
        
        Args:
            file_type (str): Type of file to browse for
            string_var (StringVar): StringVar to update with the selected path
        """
        filename = filedialog.askopenfilename(
            title=f"Select {file_type} File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            string_var.set(filename)
    
    def browse_directory(self, directory_type, string_var):
        """
        Browse for a directory and update the corresponding path.
        
        Args:
            directory_type (str): Type of directory to browse for
            string_var (StringVar): StringVar to update with the selected path
        """
        directory = filedialog.askdirectory(title=f"Select {directory_type} Directory")
        if directory:
            string_var.set(directory)
    
    def load_initial_prompts(self):
        """Load initial prompts if paths are set."""
        # Load system prompt
        system_prompt_path = self.string_vars["system_prompt_path"].get()
        if system_prompt_path and os.path.exists(system_prompt_path):
            try:
                content = self.document_processor.read_text_file(system_prompt_path)
                self.system_prompt_editor.delete(1.0, tk.END)
                self.system_prompt_editor.insert(tk.END, content)
            except Exception as e:
                print(f"Error loading system prompt: {e}")
        
        # Load user prompt
        user_prompt_path = self.string_vars["user_prompt_path"].get()
        if user_prompt_path and os.path.exists(user_prompt_path):
            try:
                content = self.document_processor.read_text_file(user_prompt_path)
                self.user_prompt_editor.delete(1.0, tk.END)
                self.user_prompt_editor.insert(tk.END, content)
            except Exception as e:
                print(f"Error loading user prompt: {e}")
    
    def load_system_prompt(self):
        """Load system prompt from the specified path."""
        path = self.string_vars["system_prompt_path"].get()
        if path and os.path.exists(path):
            try:
                content = self.document_processor.read_text_file(path)
                self.system_prompt_editor.delete(1.0, tk.END)
                self.system_prompt_editor.insert(tk.END, content)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load system prompt: {e}")
        else:
            tk.messagebox.showwarning("Warning", "Please specify a valid system prompt path.")
    
    def save_system_prompt(self):
        """Save system prompt to the specified path."""
        path = self.string_vars["system_prompt_path"].get()
        if path:
            try:
                content = self.system_prompt_editor.get(1.0, tk.END)
                self.document_processor.write_text_file(path, content)
                tk.messagebox.showinfo("Success", "System prompt saved successfully.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save system prompt: {e}")
        else:
            tk.messagebox.showwarning("Warning", "Please specify a system prompt path.")
    
    def load_user_prompt(self):
        """Load user prompt from the specified path."""
        path = self.string_vars["user_prompt_path"].get()
        if path and os.path.exists(path):
            try:
                content = self.document_processor.read_text_file(path)
                self.user_prompt_editor.delete(1.0, tk.END)
                self.user_prompt_editor.insert(tk.END, content)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load user prompt: {e}")
        else:
            tk.messagebox.showwarning("Warning", "Please specify a valid user prompt path.")
    
    def save_user_prompt(self):
        """Save user prompt to the specified path."""
        path = self.string_vars["user_prompt_path"].get()
        if path:
            try:
                content = self.user_prompt_editor.get(1.0, tk.END)
                self.document_processor.write_text_file(path, content)
                tk.messagebox.showinfo("Success", "User prompt saved successfully.")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save user prompt: {e}")
        else:
            tk.messagebox.showwarning("Warning", "Please specify a user prompt path.")
            
    def refresh_models(self):
        """Refresh available models from OpenAI API."""
        api_key = self.string_vars["api_key"].get()
        if not api_key:
            tk.messagebox.showwarning("API Key Required", "Please enter your OpenAI API key first.")
            return
        
        # Show loading dialog
        loading = tk.Toplevel(self)
        loading.title("Fetching Models")
        loading.geometry("300x100")
        loading.transient(self)
        loading.grab_set()
        
        status_var = tk.StringVar(value="Fetching available models...")
        ttk.Label(loading, textvariable=status_var, padding=20).pack()
        
        progress = ttk.Progressbar(loading, mode="indeterminate")
        progress.pack(fill="x", padx=20)
        progress.start()
        
        # Add cancel button
        ttk.Button(loading, text="Cancel", command=loading.destroy).pack(pady=10)
        
        # Set a timeout flag
        fetch_complete = False
        
        # Timeout function
        def check_timeout():
            if not fetch_complete and loading.winfo_exists():
                loading.destroy()
                tk.messagebox.showwarning("Timeout", 
                                       "Request to fetch models timed out.\n"
                                       "Using default models instead.")
                self.model_dropdown['values'] = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
        
        # Set 10 second timeout
        timeout_id = self.winfo_toplevel().after(10000, check_timeout)
        
        def fetch_models():
            nonlocal fetch_complete
            try:
                from openai import OpenAI
                import httpx
                
                # Use timeout for the API request
                client = OpenAI(
                    api_key=api_key,
                    timeout=httpx.Timeout(8.0)  # 8 second timeout for requests
                )
                
                # Update status
                self.winfo_toplevel().after(0, lambda: status_var.set("Connecting to OpenAI API..."))
                
                models = client.models.list()
                
                # Filter for chat models
                chat_models = [model.id for model in models.data 
                              if model.id.startswith(('gpt-3.5', 'gpt-4'))]
                
                # Sort models: put gpt-4 first, then gpt-3.5
                gpt4_models = sorted([m for m in chat_models if m.startswith('gpt-4')])
                gpt35_models = sorted([m for m in chat_models if m.startswith('gpt-3.5')])
                
                self.available_models = gpt4_models + gpt35_models
                
                # Mark as complete to avoid timeout
                fetch_complete = True
                
                # Cancel timeout
                self.winfo_toplevel().after_cancel(timeout_id)
                
                # Update dropdown on main thread
                self.winfo_toplevel().after(0, lambda: self._update_model_dropdown(loading))
            except Exception as e:
                # Mark as complete to avoid timeout
                fetch_complete = True
                
                # Cancel timeout
                self.winfo_toplevel().after_cancel(timeout_id)
                
                # Handle error on main thread
                self.winfo_toplevel().after(0, lambda: self._handle_refresh_error(e, loading))
        
        # Run in thread to avoid blocking UI
        import threading
        threading.Thread(target=fetch_models, daemon=True).start()
    
    def _update_model_dropdown(self, loading_dialog):
        """Update model dropdown with fetched models."""
        try:
            # Check if dialog still exists before trying to destroy it
            if loading_dialog.winfo_exists():
                if self.available_models:
                    self.model_dropdown['values'] = self.available_models
                    loading_dialog.destroy()
                    tk.messagebox.showinfo("Models Updated", f"Found {len(self.available_models)} available models.")
                else:
                    loading_dialog.destroy()
                    tk.messagebox.showwarning("No Models Found", "No compatible models were found. Using default models.")
                    self.model_dropdown['values'] = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
            else:
                # Dialog was already closed (e.g., by user or timeout)
                if self.available_models:
                    self.model_dropdown['values'] = self.available_models
                else:
                    self.model_dropdown['values'] = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
        except Exception:
            # Handle any unexpected errors
            self.model_dropdown['values'] = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
    
    def _handle_refresh_error(self, error, loading_dialog):
        """Handle errors when refreshing models."""
        try:
            # Check if dialog still exists before trying to destroy it
            if loading_dialog.winfo_exists():
                loading_dialog.destroy()
            
            # Show error message
            tk.messagebox.showerror("Error", f"Failed to fetch models: {str(error)}")
            
            # Fall back to default models
            self.model_dropdown['values'] = ["gpt-4-turbo", "gpt-4o", "gpt-3.5-turbo"]
        except Exception:
            # Dialog was already destroyed or other error
            pass
    
    def manage_models(self):
        """Open dialog to manage models."""
        # Create a new dialog window
        dialog = tk.Toplevel(self)
        dialog.title("Manage Models")
        dialog.geometry("500x400")
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()  # Make dialog modal
        
        # Create a frame for the model list
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Description label
        ttk.Label(frame, text="Manage the available models for AI Assessor", 
                 wraplength=480).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Create a model list with scrollbar
        list_frame = ttk.Frame(frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a listbox with current models
        model_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=10)
        model_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=model_listbox.yview)
        
        # Populate the listbox with current models
        for model_name in self.config_manager.config["Models"].keys():
            model_listbox.insert(tk.END, model_name)
        
        # Frame for new model addition
        add_frame = ttk.Frame(frame)
        add_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Label(add_frame, text="Model Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        model_name_var = tk.StringVar()
        model_name_entry = ttk.Entry(add_frame, textvariable=model_name_var)
        model_name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(add_frame, text="Model ID:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        model_id_var = tk.StringVar()
        model_id_entry = ttk.Entry(add_frame, textvariable=model_id_var)
        model_id_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Buttons for adding/removing models
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        
        def add_model():
            name = model_name_var.get().strip()
            model_id = model_id_var.get().strip()
            
            if not name or not model_id:
                tk.messagebox.showwarning("Warning", "Please enter both a model name and ID.")
                return
                
            # Add to config
            self.config_manager.set_value("Models", name, model_id)
            self.config_manager.save()
            
            # Add to listbox
            model_listbox.insert(tk.END, name)
            
            # Clear entries
            model_name_var.set("")
            model_id_var.set("")
            
            # Update dropdown in main view
            self.model_dropdown["values"] = list(self.config_manager.config["Models"].keys())
            
            tk.messagebox.showinfo("Success", f"Added model: {name}")
        
        def remove_model():
            # Get selected model
            selected = model_listbox.curselection()
            if not selected:
                tk.messagebox.showwarning("Warning", "Please select a model to remove.")
                return
                
            model_name = model_listbox.get(selected[0])
            
            # Confirm removal
            if tk.messagebox.askyesno("Confirm", f"Are you sure you want to remove {model_name}?"):
                # Remove from config
                if self.config_manager.config.has_option("Models", model_name):
                    self.config_manager.config.remove_option("Models", model_name)
                    self.config_manager.save()
                
                # Remove from listbox
                model_listbox.delete(selected[0])
                
                # Update dropdown in main view
                self.model_dropdown["values"] = list(self.config_manager.config["Models"].keys())
                
                tk.messagebox.showinfo("Success", f"Removed model: {model_name}")
        
        ttk.Button(buttons_frame, text="Add Model", command=add_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Remove Selected", command=remove_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Configure grid weights
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Make dialog modal
        dialog.wait_window()