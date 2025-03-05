import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, Listbox, Scrollbar, Text
from config_manager import read_config, write_config
from utils import read_text_file, write_text_file, read_word_document
from marking import grade_submission, grade_all_submissions


def update_file_list(file_list, submissions_folder_path):
    file_list.delete(0, tk.END)
    if os.path.exists(submissions_folder_path.get()) and os.path.isdir(
        submissions_folder_path.get()
    ):
        for file in os.listdir(submissions_folder_path.get()):
            if file.endswith(".docx"):
                file_list.insert(tk.END, file)
    else:
        print("Invalid submissions folder path.")


def on_tab_selected(event):
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")
    if tab_text == "Grading":
        update_file_list(file_list, submissions_folder)


def load_rubric_for_editing(rubric_path_variable, text_widget):
    filename = filedialog.askopenfilename(
        title="Select Rubric File",
        filetypes=[("Word files", "*.docx"), ("All files", "*.*")],
    )
    if filename:
        rubric_content = read_word_document(filename)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, rubric_content)
        rubric_path_variable.set(filename)  # Update the rubric path variable


def load_file_for_editing(file_type, text_widget, file_path_variable):
    filename = filedialog.askopenfilename(
        title=f"Select {file_type} File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if filename:
        content = read_text_file(filename)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, content)
        file_path_variable = filename  # Update the file path variable


def save_file(text_widget, file_path_variable):
    content = text_widget.get("1.0", tk.END)
    filename = file_path_variable
    if filename:
        write_text_file(filename, content)
        messagebox.showinfo("Success", "File saved successfully.")
    else:
        messagebox.showerror("Error", "No file loaded.")


def run_marking(
    api_key,
    system_prompt_path,
    user_prompt_path,
    submissions_folder_path,
    all_students=False,
):
    system_prompt = read_text_file(system_prompt_path.get())
    user_prompt = read_text_file(user_prompt_path.get())
    submissions_folder = submissions_folder_path.get()

    if all_students:
        grade_all_submissions(
            api_key.get(), system_prompt, user_prompt, submissions_folder
        )
    else:
        student_file = filedialog.askopenfilename(
            initialdir=submissions_folder,
            title="Select Student File",
            filetypes=[("Word files", "*.docx"), ("All files", "*.*")],
        )
        if student_file:
            grade_submission(api_key.get(), system_prompt, user_prompt, student_file)


import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import os

gpt_version_var = None
temperature_entry = None


def setup_tab1(
    parent,
    api_key,
    system_prompt_path,
    user_prompt_path,
    support_folder,
    submissions_folder,
    output_folder,
):
    # Configure the grid layout
    tk.Label(parent, text="OpenAI API Key:").grid(row=0, column=0, sticky="w")
    tk.Entry(parent, textvariable=api_key).grid(row=0, column=1, sticky="ew")

    tk.Label(parent, text="System Prompt Path:").grid(row=1, column=0, sticky="w")
    tk.Entry(parent, textvariable=system_prompt_path).grid(row=1, column=1, sticky="ew")

    tk.Label(parent, text="User Prompt Path:").grid(row=2, column=0, sticky="w")
    tk.Entry(parent, textvariable=user_prompt_path).grid(row=2, column=1, sticky="ew")

    tk.Label(parent, text="Support Files Folder:").grid(row=3, column=0, sticky="w")
    tk.Entry(parent, textvariable=support_folder).grid(row=3, column=1, sticky="ew")

    tk.Label(parent, text="Submissions Folder:").grid(row=4, column=0, sticky="w")
    tk.Entry(parent, textvariable=submissions_folder).grid(row=4, column=1, sticky="ew")

    tk.Label(parent, text="Output Folder:").grid(row=5, column=0, sticky="w")
    tk.Entry(parent, textvariable=output_folder).grid(row=5, column=1, sticky="ew")

    # Add radio buttons for GPT-3 and GPT-4
    global gpt_version_var
    gpt_version_var = tk.StringVar(value="GPT-3")  # Default to GPT-3
    ttk.Radiobutton(parent, text="GPT-3", variable=gpt_version_var, value="GPT-3").grid(
        row=6, column=0, sticky="w"
    )
    ttk.Radiobutton(parent, text="GPT-4", variable=gpt_version_var, value="GPT-4").grid(
        row=6, column=1, sticky="w"
    )

    # Add a field for Temperature input
    temperature_label = ttk.Label(parent, text="Temperature (0 to 1):")
    temperature_label.grid(row=7, column=0, sticky="w")
    global temperature_entry
    temperature_entry = ttk.Entry(parent)
    temperature_entry.grid(row=7, column=1, sticky="ew")

    # System Prompt Editor
    tk.Label(parent, text="System Prompt:").grid(row=8, column=0, sticky="w")
    system_prompt_editor = scrolledtext.ScrolledText(parent, height=10)
    system_prompt_editor.grid(row=8, column=0, columnspan=2, sticky="ew")

    # Load System Prompt if path is set and file exists
    system_prompt_file = system_prompt_path.get()
    if system_prompt_file and os.path.isfile(system_prompt_file):
        system_prompt_content = read_text_file(system_prompt_file)
        system_prompt_editor.insert(tk.END, system_prompt_content)

    tk.Button(
        parent,
        text="Load System Prompt",
        command=lambda: load_file_for_editing(
            "System Prompt", system_prompt_editor, system_prompt_path
        ),
    ).grid(row=9, column=0)
    tk.Button(
        parent,
        text="Save System Prompt",
        command=lambda: save_file(system_prompt_editor, system_prompt_path.get()),
    ).grid(row=9, column=1)

    # User Prompt Editor
    tk.Label(parent, text="User Prompt:").grid(row=10, column=0, sticky="w")
    user_prompt_editor = scrolledtext.ScrolledText(parent, height=10)
    user_prompt_editor.grid(row=11, column=0, columnspan=2, sticky="ew")

    # Load User Prompt if path is set and file exists
    user_prompt_file = user_prompt_path.get()
    if user_prompt_file and os.path.isfile(user_prompt_file):
        user_prompt_content = read_text_file(user_prompt_file)
        user_prompt_editor.insert(tk.END, user_prompt_content)

    tk.Button(
        parent,
        text="Load User Prompt",
        command=lambda: load_file_for_editing(
            "User Prompt", user_prompt_editor, user_prompt_path
        ),
    ).grid(row=12, column=0)
    tk.Button(
        parent,
        text="Save User Prompt",
        command=lambda: save_file(user_prompt_editor, user_prompt_path.get()),
    ).grid(row=12, column=1)


def display_selected_file(
    event,
    file_list,
    submission_display,
    feedback_display,
    submissions_folder,
    output_folder,
):
    selected_index = file_list.curselection()

    # Clear the displays if no file is selected
    if not selected_index:
        submission_display.delete(1.0, tk.END)
        feedback_display.delete(1.0, tk.END)
        return

    # Continue with your existing logic if an item is selected
    filename = file_list.get(selected_index[0])
    submission_file = os.path.join(submissions_folder.get(), filename)
    submission_content = read_word_document(submission_file)
    submission_display.delete(1.0, tk.END)
    submission_display.insert(tk.END, submission_content)

    feedback_filename = filename.replace(".docx", "_feedback.txt")
    feedback_file = os.path.join(output_folder.get(), feedback_filename)
    if os.path.exists(feedback_file):
        feedback_content = read_text_file(feedback_file)
    else:
        feedback_content = "Feedback not available."
    feedback_display.delete(1.0, tk.END)
    feedback_display.insert(tk.END, feedback_content)


def update_file_list(file_list, folder_path):
    file_list.delete(0, tk.END)

    if (
        folder_path
        and os.path.exists(folder_path.get())
        and os.path.isdir(folder_path.get())
    ):
        for file in os.listdir(folder_path.get()):
            if file.endswith(".docx"):
                file_list.insert(tk.END, file)
    else:
        print("Invalid or empty submissions folder path.")


def mark_selected_files(
    api_key,
    system_prompt_path,
    user_prompt_path,
    support_folder,
    submissions_folder,
    file_list,
    model,
    temperature,
):
    selected_indices = file_list.curselection()
    if selected_indices:
        system_prompt = read_text_file(system_prompt_path)
        user_prompt = read_text_file(user_prompt_path)
        for index in selected_indices:
            filename = file_list.get(index)
            submission_file = os.path.join(submissions_folder, filename)

            # Grade the individual submission
            grade_submission(
                api_key,
                system_prompt,
                user_prompt,
                submission_file,
                support_folder,
                output_folder,
                model,
                temperature,
            )

            # Optionally, you can update the display here for each submission
            # This is up to your application's requirements and design

        messagebox.showinfo("Success", "Selected files have been graded.")


file_list = None


def setup_tab2(
    parent,
    api_key,
    system_prompt_path,
    user_prompt_path,
    support_folder,
    submissions_folder,
    output_folder,
):
    # File List Pane
    file_list_frame = tk.Frame(parent)
    file_list_scrollbar = Scrollbar(file_list_frame, orient="vertical")
    global file_list
    file_list = Listbox(
        file_list_frame, yscrollcommand=file_list_scrollbar.set, selectmode="multiple"
    )
    file_list_scrollbar.config(command=file_list.yview)
    file_list_scrollbar.pack(side="right", fill="y")
    file_list.pack(side="left", fill="both", expand=True)
    file_list_frame.pack(side="left", fill="both", expand=True)
    # tk.Label(parent, text="Submissions").pack()

    # Button to mark selected files
    mark_button = tk.Button(
        parent,
        text="Mark Selected Files",
        command=lambda: mark_selected_files(
            api_key.get(),
            system_prompt_path.get(),
            user_prompt_path.get(),
            support_folder.get(),
            submissions_folder.get(),
            file_list,
            gpt_version_var.get(),
            temperature=float(temperature_entry.get()),
        ),
    )
    mark_button.pack()

    # Update file list when tab is selected
    update_file_list(file_list, submissions_folder)

    # Submission Display Pane
    submission_display = Text(parent, height=15)
    submission_display.pack(side="left", fill="both", expand=True)
    # tk.Label(parent, text="Submission Content").pack()

    # Feedback Display Pane
    feedback_display = Text(parent, height=15)
    feedback_display.pack(side="left", fill="both", expand=True)
    # tk.Label(parent, text="Feedback").pack()

    # Bind listbox selection event
    file_list.bind(
        "<<ListboxSelect>>",
        lambda event: display_selected_file(
            event,
            file_list,
            submission_display,
            feedback_display,
            submissions_folder,
            output_folder,
        ),
    )


# Main Application
root = tk.Tk()
root.title("AI Assessor")

# Variables for configuration paths and API key
system_prompt_path = tk.StringVar()
user_prompt_path = tk.StringVar()
support_folder = tk.StringVar()
submissions_folder = tk.StringVar()
output_folder = tk.StringVar()
api_key = tk.StringVar()

# Load the configuration at the start of your script
config = read_config("config.ini")

# Reading paths from the config file
system_prompt_path.set(config["Paths"]["SystemPromptPath"])
user_prompt_path.set(config["Paths"]["UserPromptPath"])
support_folder.set(config["Paths"]["SupportFolder"])
submissions_folder.set(config["Paths"]["SubmissionsFolder"])
output_folder.set(config["Paths"]["OutputFolder"])

from dotenv import load_dotenv

load_dotenv()  # This loads the .env file
api_key.set(os.getenv("OPENAPI_KEY"))


tab_control = ttk.Notebook(root)

# Setup the tabs
tab_control = ttk.Notebook(root)
tab_control.bind("<<NotebookTabChanged>>", on_tab_selected)

# Tab 1: Configuration and Prompts
tab1 = ttk.Frame(tab_control)
setup_tab1(
    tab1,
    api_key,
    system_prompt_path,
    user_prompt_path,
    support_folder,
    submissions_folder,
    output_folder,
)
tab_control.add(tab1, text="Configuration and Prompts")

# Tab 2: Grading
tab2 = ttk.Frame(tab_control)
# Assuming file_list and submissions_folder_path are accessible here
setup_tab2(
    tab2,
    api_key,
    system_prompt_path,
    user_prompt_path,
    support_folder,
    submissions_folder,
    output_folder,
)
tab_control.add(tab2, text="Grading")

tab_control.pack(expand=1, fill="both")

root.mainloop()
