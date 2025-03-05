#!/usr/bin/env python3
"""
Build script for creating a standalone executable with PyInstaller.
"""

import os
import sys
import shutil
import subprocess

def create_executable():
    """
    Create a standalone executable using PyInstaller.
    """
    print("Building AI Assessor standalone executable...")
    
    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
    # Verify the PyInstaller executable is in PATH
    pyinstaller_cmd = "pyinstaller"
    
    # On Windows, we need to be more careful about finding the executable
    if sys.platform.startswith('win'):
        # Try with python -m PyInstaller instead of direct command
        pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]
        print(f"Using Python module form for PyInstaller on Windows: {pyinstaller_cmd}")
    
    # Create dist directory if it doesn't exist
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Create a simple icon if not present
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        try:
            # Try to create a simple icon using PIL
            from PIL import Image, ImageDraw
            
            # Create a 64x64 image with a simple A letter
            img = Image.new('RGBA', (64, 64), color=(0, 120, 212, 255))
            d = ImageDraw.Draw(img)
            d.text((20, 20), "A", fill=(255, 255, 255, 255))
            
            # Save as .ico
            img.save(icon_path)
            print(f"Created simple icon: {icon_path}")
        except ImportError:
            print("PIL not found, skipping icon creation.")
            icon_path = None
    
    # Prepare PyInstaller command
    if isinstance(pyinstaller_cmd, list):
        # For Windows using Python module form
        cmd = pyinstaller_cmd + [
            "--clean",
            "--name=AI_Assessor",
            "--onefile",
            "--windowed",
        ]
    else:
        # For direct command execution
        cmd = [
            pyinstaller_cmd,
            "--clean",
            "--name=AI_Assessor",
            "--onefile",
            "--windowed",
        ]
    
    # Add icon if available
    if icon_path and os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
    
    # Check for config.ini and create from template if missing
    if not os.path.exists("config.ini") and os.path.exists("config.ini.template"):
        print("config.ini not found, creating from template...")
        shutil.copy("config.ini.template", "config.ini")
    
    # Add data files - handle path separators differently on Windows vs Unix
    separator = ";" if sys.platform.startswith('win') else ":"
    
    # Build data additions with appropriate separator
    data_additions = [
        f"--add-data=aiassessor/core{separator}aiassessor/core",
        f"--add-data=aiassessor/ui{separator}aiassessor/ui",
        f"--add-data=aiassessor/utils{separator}aiassessor/utils",
        f"--add-data=aiassessor/config{separator}aiassessor/config",
    ]
    
    # Add config files if they exist
    if os.path.exists("config.ini"):
        data_additions.append(f"--add-data=config.ini{separator}.")
    if os.path.exists("config.ini.template"):
        data_additions.append(f"--add-data=config.ini.template{separator}.")
        
    # Add default prompt files
    default_prompts_dir = "default_prompts"
    if not os.path.exists(default_prompts_dir):
        os.makedirs(default_prompts_dir)
        
    # Create default system prompt if it doesn't exist
    default_system_prompt = os.path.join(default_prompts_dir, "system_prompt.txt")
    if not os.path.exists(default_system_prompt):
        with open(default_system_prompt, "w") as f:
            f.write("""You are an expert in evaluating student assignments. Your task is to provide detailed feedback and grading for a student's submission, based on the rubric provided.

Please evaluate the work objectively, considering the quality of reasoning, accuracy of information, clarity of expression, and adherence to the requirements.

Your feedback should be:
1. Specific and detailed
2. Constructive and actionable
3. Balanced, noting both strengths and areas for improvement

Format your response as follows:
- Overall assessment (2-3 sentences summarizing the work)
- Strengths (bullet points of what was done well)
- Areas for improvement (bullet points with specific suggestions)
- Grade (a letter grade or numerical score, with brief justification)
""")
    
    # Create default user prompt if it doesn't exist
    default_user_prompt = os.path.join(default_prompts_dir, "user_prompt.txt")
    if not os.path.exists(default_user_prompt):
        with open(default_user_prompt, "w") as f:
            f.write("""Please evaluate the following student submission.

The assignment asked students to write a short essay analyzing the main themes of a literary work they read this semester. They were instructed to identify at least three themes, provide textual evidence for each, and explain the significance of these themes to the overall work.

Grading criteria:
- Identification of at least three relevant themes (30%)
- Quality and relevance of textual evidence (30%)
- Depth of analysis and explanation of significance (30%)
- Organization and clarity of writing (10%)

Please provide a detailed assessment, including strengths, areas for improvement, and a final grade out of 100.

Below is the student's submission:
""")
    
    # Add default prompts to distribution
    data_additions.append(f"--add-data={default_prompts_dir}{separator}{default_prompts_dir}")
    
    cmd.extend(data_additions)
    
    # Add the main script
    cmd.append("standalone.py")
    
    # Run PyInstaller
    print("Running PyInstaller with command:")
    # Format the command for better readability
    if isinstance(cmd[0], list):
        cmd_str = f"{' '.join(cmd[0])} {' '.join(cmd[1:])}"
    else:
        cmd_str = " ".join(cmd)
    print(cmd_str)
    
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Try installing PyInstaller manually: pip install pyinstaller")
        print("2. Make sure PyInstaller is in your PATH")
        print("3. Try running: python -m PyInstaller standalone.py")
        return
    except subprocess.CalledProcessError as e:
        print(f"Error during PyInstaller execution: {e}")
        return
    
    print("Creating sample prompts directory...")
    # Create sample prompts directory in dist
    prompts_dir = os.path.join("dist", "prompts")
    if not os.path.exists(prompts_dir):
        os.makedirs(prompts_dir)
    
    # Create sample system prompt
    with open(os.path.join(prompts_dir, "system_prompt.txt"), "w") as f:
        f.write("""You are an expert in evaluating student assignments. Your task is to provide detailed feedback and grading for a student's submission, based on the rubric provided.

Please evaluate the work objectively, considering the quality of reasoning, accuracy of information, clarity of expression, and adherence to the requirements.

Your feedback should be:
1. Specific and detailed
2. Constructive and actionable
3. Balanced, noting both strengths and areas for improvement

Format your response as follows:
- Overall assessment (2-3 sentences summarizing the work)
- Strengths (bullet points of what was done well)
- Areas for improvement (bullet points with specific suggestions)
- Grade (a letter grade or numerical score, with brief justification)
""")
    
    # Create sample user prompt
    with open(os.path.join(prompts_dir, "user_prompt.txt"), "w") as f:
        f.write("""Please evaluate the following student submission.

The assignment asked students to write a short essay analyzing the main themes of a literary work they read this semester. They were instructed to identify at least three themes, provide textual evidence for each, and explain the significance of these themes to the overall work.

Grading criteria:
- Identification of at least three relevant themes (30%)
- Quality and relevance of textual evidence (30%)
- Depth of analysis and explanation of significance (30%)
- Organization and clarity of writing (10%)

Please provide a detailed assessment, including strengths, areas for improvement, and a final grade out of 100.

Below is the student's submission:
""")
    
    # Create README for the distribution
    with open(os.path.join("dist", "README.txt"), "w") as f:
        f.write("""AI ASSESSOR
==========

Thank you for installing AI Assessor!

Quick Start:
1. Run AI_Assessor.exe
2. In the Configuration tab, enter your OpenAI API key
3. Set paths for system prompt, user prompt, submissions folder, and output folder
4. Sample prompts are provided in the 'prompts' folder
5. Switch to the Grading tab to grade submissions

The config.ini file stores your settings and can be edited directly if needed.

For more information and support, visit: https://github.com/yourusername/aiassessor
""")
    
    print("Build completed successfully!")
    print(f"Executable created at: {os.path.join('dist', 'AI_Assessor.exe')}")
    print("Sample prompts and README created in the dist folder.")

if __name__ == "__main__":
    create_executable()