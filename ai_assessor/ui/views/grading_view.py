import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ...utils.file_utils import FileUtils
from ...utils.document_processor import DocumentProcessor

class GradingView(ttk.Frame):
    """
    Grading tab of the application.
    """
    
    def __init__(self, parent, assessor, config_manager, string_vars):
        """
        Initialize the grading view.
        
        Args:
            parent: The parent widget
            assessor: The assessor instance
            config_manager: The configuration manager
            string_vars: Dictionary of StringVar objects for configuration
        """
        super().__init__(parent)
        self.assessor = assessor
        self.config_manager = config_manager
        self.string_vars = string_vars
        self.document_processor = DocumentProcessor()
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI elements for the grading tab."""
        # Configure layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=3)
        self.rowconfigure(1, weight=1)
        
        # File list frame
        ttk.Label(self, text="Submissions:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        list_frame = ttk.Frame(self)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add scrollbar to file list
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode="extended")
        self.file_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_list.yview)
        
        # Bind selection event
        self.file_list.bind("<<ListboxSelect>>", self.on_file_selected)
        
        # Buttons for grading
        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(button_frame, text="Grade Selected", command=self.grade_selected).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Grade All", command=self.grade_all).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Refresh List", command=self.update_file_list).pack(side="left", padx=5, pady=5)
        
        # Content display
        ttk.Label(self, text="Submission Content:").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.submission_display = tk.Text(self, wrap="word")
        self.submission_display.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        ttk.Label(self, text="Feedback:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.feedback_display = tk.Text(self, wrap="word")
        self.feedback_display.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var).grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Load initial file list
        self.update_file_list()
    
    def update_file_list(self):
        """Update the list of submission files."""
        # Clear existing list
        self.file_list.delete(0, tk.END)
        
        # Get submissions folder path
        submissions_folder = self.string_vars["submissions_folder"].get()
        
        if submissions_folder and os.path.exists(submissions_folder) and os.path.isdir(submissions_folder):
            try:
                # Get all docx files
                docx_files = FileUtils.get_docx_files(submissions_folder)
                
                # Add to listbox
                for filename in docx_files:
                    self.file_list.insert(tk.END, filename)
                
                self.status_var.set(f"Found {len(docx_files)} submission files")
            except Exception as e:
                self.status_var.set(f"Error listing files: {str(e)}")
        else:
            self.status_var.set("Invalid submissions folder path")
    
    def on_file_selected(self, event):
        """
        Handle file selection from the list.
        
        Args:
            event: The selection event
        """
        # Get selected indices
        selected_indices = self.file_list.curselection()
        
        # Clear displays if nothing selected
        if not selected_indices:
            self.submission_display.delete(1.0, tk.END)
            self.feedback_display.delete(1.0, tk.END)
            return
        
        # Get the selected filename
        filename = self.file_list.get(selected_indices[0])
        
        # Display submission content
        self.display_submission(filename)
        
        # Display feedback if available
        self.display_feedback(filename)
    
    def display_submission(self, filename):
        """
        Display the content of a submission file.
        
        Args:
            filename (str): Name of the submission file
        """
        submissions_folder = self.string_vars["submissions_folder"].get()
        
        if submissions_folder and os.path.exists(submissions_folder):
            try:
                # Get full path to submission
                submission_path = os.path.join(submissions_folder, filename)
                
                # Read content
                content = self.document_processor.read_word_document(submission_path)
                
                # Display content
                self.submission_display.delete(1.0, tk.END)
                self.submission_display.insert(tk.END, content)
                
                self.status_var.set(f"Loaded submission: {filename}")
            except Exception as e:
                self.status_var.set(f"Error reading submission: {str(e)}")
                messagebox.showerror("Error", f"Failed to read submission: {str(e)}")
    
    def display_feedback(self, filename):
        """
        Display feedback for a submission if available.
        
        Args:
            filename (str): Name of the submission file
        """
        output_folder = self.string_vars["output_folder"].get()
        
        if output_folder and os.path.exists(output_folder):
            # Get feedback filename
            feedback_filename = filename.replace(".docx", "_feedback.txt")
            feedback_path = os.path.join(output_folder, feedback_filename)
            
            # Clear feedback display
            self.feedback_display.delete(1.0, tk.END)
            
            # Check if feedback exists
            if os.path.exists(feedback_path):
                try:
                    # Read and display feedback
                    content = self.document_processor.read_text_file(feedback_path)
                    self.feedback_display.insert(tk.END, content)
                except Exception as e:
                    self.feedback_display.insert(tk.END, f"Error reading feedback: {str(e)}")
            else:
                self.feedback_display.insert(tk.END, "Feedback not available. Use 'Grade Selected' to assess this submission.")
    
    def grade_selected(self):
        """Grade the selected submissions."""
        # Get selected indices
        selected_indices = self.file_list.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one submission to grade.")
            return
            
        # Number of submissions to grade
        total_submissions = len(selected_indices)
            
        # Create a progress dialog
        progress_window = tk.Toplevel(self)
        progress_window.title("Grading Progress")
        progress_window.geometry("400x200")
        progress_window.transient(self)
        progress_window.grab_set()
        progress_window.resizable(False, False)
        
        # Center the window
        progress_window.update_idletasks()
        window_width = progress_window.winfo_width()
        window_height = progress_window.winfo_height()
        x_offset = (progress_window.winfo_screenwidth() - window_width) // 2
        y_offset = (progress_window.winfo_screenheight() - window_height) // 2
        progress_window.geometry(f"+{x_offset}+{y_offset}")
        
        # Create a frame for the progress information
        frame = ttk.Frame(progress_window, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Add a label showing what's being graded
        current_file_var = tk.StringVar(value="Initializing...")
        ttk.Label(frame, text="Current File:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        ttk.Label(frame, textvariable=current_file_var, font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        # Add progress bar
        ttk.Label(frame, text="Overall Progress:").grid(row=1, column=0, sticky="w", pady=(10, 5))
        progress_var = tk.IntVar(value=0)
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=total_submissions, length=300)
        progress_bar.grid(row=1, column=1, sticky="ew", pady=(10, 5))
        
        # Add submission count info
        count_var = tk.StringVar(value=f"0/{total_submissions} completed")
        ttk.Label(frame, textvariable=count_var).grid(row=2, column=1, sticky="e", pady=(5, 15))
        
        # Add status message
        status_var = tk.StringVar(value="Starting...")
        ttk.Label(frame, textvariable=status_var, wraplength=350).grid(row=3, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Add activity indicator
        activity_frame = ttk.Frame(frame)
        activity_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        activity_bar = ttk.Progressbar(activity_frame, mode="indeterminate", length=300)
        activity_bar.pack()
        activity_bar.start()
        
        # Configure grid for frame
        frame.columnconfigure(1, weight=1)
        
        # Force update to show the window
        progress_window.update()
        
        # Get configurations
        api_key = self.string_vars["api_key"].get()
        system_prompt_path = self.string_vars["system_prompt_path"].get()
        user_prompt_path = self.string_vars["user_prompt_path"].get()
        support_folder = self.string_vars["support_folder"].get()
        submissions_folder = self.string_vars["submissions_folder"].get()
        output_folder = self.string_vars["output_folder"].get()
        model = self.string_vars["model"].get()
        
        # Run grading in a separate thread to keep UI responsive
        def run_grading():
            nonlocal progress_window
            
            try:
                # Update status 
                self.update_progress_ui(status_var, "Validating inputs...")
                
                # Validate temperature
                try:
                    temperature = float(self.string_vars["temperature"].get())
                    if temperature < 0 or temperature > 1:
                        raise ValueError("Temperature must be between 0 and 1")
                except ValueError as e:
                    self.show_error_and_close(progress_window, f"Invalid temperature value: {str(e)}")
                    return
                
                # Validate paths
                if not api_key:
                    self.show_error_and_close(progress_window, "API key is required.")
                    return
                    
                if not os.path.exists(system_prompt_path):
                    self.show_error_and_close(progress_window, "System prompt file not found.")
                    return
                    
                if not os.path.exists(user_prompt_path):
                    self.show_error_and_close(progress_window, "User prompt file not found.")
                    return
                
                # Update status
                self.update_progress_ui(status_var, "Loading prompt files...")
                
                # Read prompts
                try:
                    system_prompt = self.document_processor.read_text_file(system_prompt_path)
                    user_prompt = self.document_processor.read_text_file(user_prompt_path)
                except Exception as e:
                    self.show_error_and_close(progress_window, f"Failed to read prompts: {str(e)}")
                    return
                
                # Ensure output folder exists
                if output_folder:
                    try:
                        FileUtils.ensure_dir_exists(output_folder)
                    except Exception as e:
                        self.show_error_and_close(progress_window, f"Failed to create output folder: {str(e)}")
                        return
                
                # Process each selected submission
                success_count = 0
                fail_count = 0
                
                for i, index in enumerate(selected_indices):
                    if not progress_window.winfo_exists():
                        # User closed the window, stop processing
                        return
                        
                    filename = self.file_list.get(index)
                    submission_path = os.path.join(submissions_folder, filename)
                    
                    # Update progress UI
                    self.update_progress_ui(current_file_var, filename)
                    self.update_progress_ui(count_var, f"{i}/{total_submissions} completed")
                    self.update_progress_ui(progress_var, i)
                    self.update_progress_ui(status_var, f"Grading {filename}... (connecting to OpenAI)")
                    
                    # Update main status
                    self.update_status(f"Grading: {filename}...")
                    
                    # Grade submission
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
                            self.update_progress_ui(status_var, f"Successfully graded {filename}")
                        else:
                            fail_count += 1
                            self.update_progress_ui(status_var, f"Failed to grade {filename}: {feedback}")
                    except Exception as e:
                        fail_count += 1
                        self.update_progress_ui(status_var, f"Error grading {filename}: {str(e)}")
                
                # Final update
                self.update_progress_ui(progress_var, total_submissions)
                self.update_progress_ui(count_var, f"{total_submissions}/{total_submissions} completed")
                self.update_progress_ui(status_var, "Finalizing...")
                
                # Close progress window and show result
                self.complete_grading(progress_window, success_count, fail_count)
                
            except Exception as e:
                # Handle any unexpected errors
                self.show_error_and_close(progress_window, f"Unexpected error: {str(e)}")
        
        # Start grading in a separate thread
        import threading
        threading.Thread(target=run_grading, daemon=True).start()
    
    def update_progress_ui(self, var, value):
        """Update a tkinter variable in the main thread."""
        if isinstance(var, tk.Variable):
            var.set(value)
        else:
            # It's a progressbar value that needs to be set
            var.set(value)
        self.update_idletasks()
    
    def update_status(self, message):
        """Update the status bar message."""
        self.status_var.set(message)
        self.update_idletasks()
    
    def show_error_and_close(self, progress_window, error_message):
        """Show error message and close progress window."""
        if progress_window.winfo_exists():
            progress_window.destroy()
        messagebox.showerror("Error", error_message)
        self.status_var.set("Error: Grading failed")
    
    def complete_grading(self, progress_window, success_count, fail_count):
        """Handle completion of grading process."""
        if progress_window.winfo_exists():
            progress_window.destroy()
            
        # Update status and show result
        self.status_var.set(f"Grading completed: {success_count} succeeded, {fail_count} failed")
        messagebox.showinfo("Grading Complete", f"Graded {success_count} submissions successfully. {fail_count} failed.")
        
        # Refresh the feedback display if a submission is selected
        current_selection = self.file_list.curselection()
        if current_selection:
            self.display_feedback(self.file_list.get(current_selection[0]))
    
    def grade_all(self):
        """Grade all submissions in the folder."""
        # Get configurations
        api_key = self.string_vars["api_key"].get()
        system_prompt_path = self.string_vars["system_prompt_path"].get()
        user_prompt_path = self.string_vars["user_prompt_path"].get()
        support_folder = self.string_vars["support_folder"].get()
        submissions_folder = self.string_vars["submissions_folder"].get()
        output_folder = self.string_vars["output_folder"].get()
        model = self.string_vars["model"].get()
        
        # Validate basic settings first
        if not api_key:
            messagebox.showerror("Error", "API key is required.")
            return
            
        # Confirm with user
        file_count = self.file_list.size()
        if file_count == 0:
            messagebox.showwarning("Warning", "No submission files found.")
            return
        
        confirm = messagebox.askyesno(
            "Confirm Grading",
            f"Are you sure you want to grade all {file_count} submissions? This may take some time."
        )
        
        if not confirm:
            return
            
        # Create a progress dialog
        progress_window = tk.Toplevel(self)
        progress_window.title("Grading All Submissions")
        progress_window.geometry("450x220")
        progress_window.transient(self)
        progress_window.grab_set()
        progress_window.resizable(False, False)
        
        # Center the window
        progress_window.update_idletasks()
        window_width = progress_window.winfo_width()
        window_height = progress_window.winfo_height()
        x_offset = (progress_window.winfo_screenwidth() - window_width) // 2
        y_offset = (progress_window.winfo_screenheight() - window_height) // 2
        progress_window.geometry(f"+{x_offset}+{y_offset}")
        
        # Create a frame for the progress information
        frame = ttk.Frame(progress_window, padding=20)
        frame.pack(fill="both", expand=True)
        
        # Header
        ttk.Label(
            frame, 
            text=f"Grading {file_count} submissions", 
            font=("Helvetica", 12, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Add a label showing current status
        current_file_var = tk.StringVar(value="Initializing...")
        ttk.Label(frame, text="Current:").grid(row=1, column=0, sticky="w", pady=(0, 5))
        ttk.Label(frame, textvariable=current_file_var, font=("Helvetica", 10, "bold")).grid(row=1, column=1, sticky="w", pady=(0, 5))
        
        # Add progress bar
        ttk.Label(frame, text="Progress:").grid(row=2, column=0, sticky="w", pady=(10, 5))
        progress_var = tk.IntVar(value=0)
        progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=file_count, length=300)
        progress_bar.grid(row=2, column=1, sticky="ew", pady=(10, 5))
        
        # Add submission count info
        count_var = tk.StringVar(value=f"0/{file_count} completed")
        ttk.Label(frame, textvariable=count_var).grid(row=3, column=1, sticky="e", pady=(5, 15))
        
        # Add status message
        status_var = tk.StringVar(value="Starting grading process...")
        ttk.Label(frame, textvariable=status_var, wraplength=350).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # Add activity indicator
        activity_frame = ttk.Frame(frame)
        activity_frame.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        activity_bar = ttk.Progressbar(activity_frame, mode="indeterminate", length=300)
        activity_bar.pack()
        activity_bar.start()
        
        # Configure grid for frame
        frame.columnconfigure(1, weight=1)
        
        # Force update to show the window
        progress_window.update()
        
        # Run grading in a separate thread to keep UI responsive
        def run_grading():
            nonlocal progress_window
            
            try:
                # Update status 
                self.update_progress_ui(status_var, "Validating inputs...")
                
                # Validate temperature
                try:
                    temperature = float(self.string_vars["temperature"].get())
                    if temperature < 0 or temperature > 1:
                        raise ValueError("Temperature must be between 0 and 1")
                except ValueError as e:
                    self.show_error_and_close(progress_window, f"Invalid temperature value: {str(e)}")
                    return
                    
                # Validate paths
                if not os.path.exists(system_prompt_path):
                    self.show_error_and_close(progress_window, "System prompt file not found.")
                    return
                    
                if not os.path.exists(user_prompt_path):
                    self.show_error_and_close(progress_window, "User prompt file not found.")
                    return
                
                # Read prompts
                self.update_progress_ui(status_var, "Reading prompt files...")
                try:
                    system_prompt = self.document_processor.read_text_file(system_prompt_path)
                    user_prompt = self.document_processor.read_text_file(user_prompt_path)
                except Exception as e:
                    self.show_error_and_close(progress_window, f"Failed to read prompts: {str(e)}")
                    return
                
                # Get file list
                self.update_progress_ui(status_var, "Getting submission files...")
                filenames = []
                for i in range(file_count):
                    filenames.append(self.file_list.get(i))
                
                # Process submissions
                success_count = 0
                fail_count = 0
                results = {}
                
                for i, filename in enumerate(filenames):
                    if not progress_window.winfo_exists():
                        # User closed the window, stop processing
                        return
                        
                    submission_path = os.path.join(submissions_folder, filename)
                    
                    # Update progress UI
                    self.update_progress_ui(current_file_var, filename)
                    self.update_progress_ui(count_var, f"{i}/{file_count} completed")
                    self.update_progress_ui(progress_var, i)
                    self.update_progress_ui(status_var, f"Grading {filename}... (connecting to OpenAI)")
                    
                    # Update main status
                    self.update_status(f"Grading: {filename}...")
                    
                    # Grade submission
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
                        
                        # Track results
                        results[filename] = {"success": success, "feedback": feedback}
                        
                        if success:
                            success_count += 1
                            self.update_progress_ui(status_var, f"Successfully graded {filename}")
                        else:
                            fail_count += 1
                            self.update_progress_ui(status_var, f"Failed to grade {filename}")
                    except Exception as e:
                        fail_count += 1
                        results[filename] = {"success": False, "feedback": str(e)}
                        self.update_progress_ui(status_var, f"Error grading {filename}: {str(e)}")
                
                # Final update
                self.update_progress_ui(progress_var, file_count)
                self.update_progress_ui(count_var, f"{file_count}/{file_count} completed")
                self.update_progress_ui(status_var, "Finalizing...")
                
                # Close progress window and show result
                self.complete_grading(progress_window, success_count, fail_count)
                
            except Exception as e:
                # Handle any unexpected errors
                self.show_error_and_close(progress_window, f"Unexpected error: {str(e)}")
        
        # Start grading in a separate thread
        import threading
        threading.Thread(target=run_grading, daemon=True).start()