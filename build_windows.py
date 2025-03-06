#!/usr/bin/env python3
"""
Build script for creating a standalone Windows executable using PyInstaller.
Run this script on a Windows machine to create the distributable package.
"""

import os
import shutil
import subprocess
import sys

def build_windows_executable():
    """
    Build a standalone Windows executable with PyInstaller and prepare the distribution folder.
    """
    print("Beginning build process for AI Assessor Windows standalone...")
    
    # Print Python and OS information for debugging
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller installation completed.")
            
            # Verify installation
            import importlib
            importlib.invalidate_caches()
            import PyInstaller
            print(f"PyInstaller version: {PyInstaller.__version__}")
        except Exception as e:
            print(f"Error installing PyInstaller: {e}")
            print("Please try manually installing PyInstaller with: pip install pyinstaller")
            print("Then run this script again.")
            sys.exit(1)
    
    # Create build spec for PyInstaller
    print("Creating PyInstaller spec file...")
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['ai_assessor_main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# Add data files
a.datas += [('config.ini.template', 'config.ini.template', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='AI_Assessor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='icon.ico' if os.path.exists('icon.ico') else None)
"""
    
    with open("ai_assessor.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    print("Running PyInstaller...")
    try:
        # Use python -m pyinstaller to ensure we're using the installed package
        print(f"Running command: {sys.executable} -m pyinstaller --clean ai_assessor.spec")
        subprocess.run([sys.executable, "-m", "pyinstaller", "--clean", "ai_assessor.spec"], 
                      check=True, 
                      capture_output=False)
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed with error code {e.returncode}")
        print("Error output:")
        print(e.stderr if hasattr(e, 'stderr') else "No error output available")
        print("\nPlease check if PyInstaller is correctly installed and the spec file is valid.")
        print("You can try running: python -m PyInstaller --clean ai_assessor.spec")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while running PyInstaller: {e}")
        sys.exit(1)
    
    # Create distribution folder structure
    dist_folder = os.path.join("dist", "AI_Assessor")
    
    # Create necessary folders in the dist directory
    folders = ["prompts", "submissions", "support"]
    for folder in folders:
        os.makedirs(os.path.join(dist_folder, folder), exist_ok=True)
    
    # Copy example files to prompts folder
    prompts_dest = os.path.join(dist_folder, "prompts")
    for file in ["system_prompt.txt", "user_prompt.txt", "example_system_prompt.txt", "example_user_prompt.txt"]:
        source_file = os.path.join("prompts", file)
        if os.path.exists(source_file):
            shutil.copy2(source_file, os.path.join(prompts_dest, file))
    
    # Copy sample submissions
    submissions_dest = os.path.join(dist_folder, "submissions")
    submissions_src = "submissions"
    if os.path.exists(submissions_src):
        for file in os.listdir(submissions_src):
            if file.endswith(".docx"):
                shutil.copy2(os.path.join(submissions_src, file), os.path.join(submissions_dest, file))
    
    # Copy support files
    support_dest = os.path.join(dist_folder, "support")
    support_src = "support"
    if os.path.exists(support_src):
        for file in os.listdir(support_src):
            if file.endswith(".docx"):
                shutil.copy2(os.path.join(support_src, file), os.path.join(support_dest, file))
    
    # Create a default config.ini file
    config_ini_content = """[Paths]
SystemPromptPath = prompts/system_prompt.txt
UserPromptPath = prompts/user_prompt.txt
SupportFolder = support
SubmissionsFolder = submissions
OutputFolder = output

[API]
Key = 
DefaultModel = gpt-4-turbo
Temperature = 0.7

[Models]
gpt-3.5-turbo = gpt-3.5-turbo
gpt-4-turbo = gpt-4-turbo
gpt-4o = gpt-4o
"""
    
    with open(os.path.join(dist_folder, "config.ini"), "w") as f:
        f.write(config_ini_content)
    
    # Create README.txt with instructions
    readme_content = """AI Assessor - Windows Standalone Version

Quick Start Guide:
=================

1. Setup:
   - Enter your OpenAI API key in the Settings tab
   - The application is pre-configured with default folders:
     * prompts: Contains the system and user prompts
     * submissions: Place student submissions (.docx files) here
     * support: Contains rubrics and assessment guidelines

2. Usage:
   - Navigate to the Grade tab
   - Select a file to grade or click "Grade All" to process all files in the submissions folder
   - View results in the assessment panel or in the output folder

3. Configuration:
   - You can modify paths and settings in the Settings tab
   - Example prompts are included in the prompts folder

Note: Internet connection is required for the AI assessment functionality.
"""
    
    with open(os.path.join(dist_folder, "README.txt"), "w") as f:
        f.write(readme_content)
    
    # Create output folder
    os.makedirs(os.path.join(dist_folder, "output"), exist_ok=True)
    
    print("\nBuild completed successfully!")
    print(f"Standalone application created in: {os.path.abspath(dist_folder)}")
    print("To distribute to users, zip the entire AI_Assessor folder.")

if __name__ == "__main__":
    build_windows_executable()