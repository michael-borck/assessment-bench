#!/usr/bin/env python3
"""
Build script for creating a standalone Windows executable using PyInstaller.
Run this script on a Windows machine to create the distributable package.

IMPORTANT: This script should be run in a virtual environment:
1. python -m venv venv
2. venv\Scripts\activate
3. pip install -r requirements.txt
4. pip install pyinstaller
5. python build_windows.py
"""

import os
import shutil
import subprocess
import sys
import site

def build_windows_executable():
    """
    Build a standalone Windows executable with PyInstaller and prepare the distribution folder.
    """
    print("Beginning build process for AI Assessor Windows standalone...")
    
    # Print Python and OS information for debugging
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("WARNING: It's recommended to run this script in a virtual environment.")
        print("Please consider creating and activating a virtual environment first:")
        print("1. python -m venv venv")
        print("2. venv\\Scripts\\activate (Windows) or source venv/bin/activate (Unix)")
        print("3. pip install -r requirements.txt")
        print("4. pip install pyinstaller")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting. Please run the script in a virtual environment.")
            sys.exit(0)
    
    # Check PyInstaller installation
    pyinstaller_found = False
    
    # Method 1: Try importing PyInstaller
    try:
        import PyInstaller
        pyinstaller_found = True
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller module not found.")
    
    # Method 2: Check if pyinstaller executable is in PATH
    if not pyinstaller_found:
        try:
            pyinstaller_path = shutil.which("pyinstaller")
            if pyinstaller_path:
                pyinstaller_found = True
                print(f"PyInstaller executable found at: {pyinstaller_path}")
            else:
                print("PyInstaller executable not found in PATH.")
        except Exception:
            print("Failed to check for PyInstaller in PATH.")
    
    # Method 3: Check in site-packages
    if not pyinstaller_found:
        site_packages = site.getsitepackages()
        print(f"Checking site-packages directories: {site_packages}")
        for sp in site_packages:
            pyinstaller_dir = os.path.join(sp, "PyInstaller")
            if os.path.exists(pyinstaller_dir):
                pyinstaller_found = True
                print(f"PyInstaller found in site-packages: {pyinstaller_dir}")
                break
    
    # Install if not found
    if not pyinstaller_found:
        print("PyInstaller not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("PyInstaller installation completed.")
            
            # Verify installation
            import importlib
            importlib.invalidate_caches()
            try:
                import PyInstaller
                print(f"PyInstaller version: {PyInstaller.__version__}")
                pyinstaller_found = True
            except ImportError:
                print("WARNING: PyInstaller module still not available after installation.")
                
            # Check executable after installation
            pyinstaller_path = shutil.which("pyinstaller")
            if pyinstaller_path:
                print(f"PyInstaller executable now available at: {pyinstaller_path}")
                pyinstaller_found = True
        except Exception as e:
            print(f"Error installing PyInstaller: {e}")
            print("Please try manually installing PyInstaller with: pip install pyinstaller")
            print("Then run this script again.")
            sys.exit(1)
    
    if not pyinstaller_found:
        print("ERROR: Could not find or install PyInstaller.")
        print("Please install it manually with: pip install pyinstaller")
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
        # Try different methods to run PyInstaller
        pyinstaller_success = False
        
        # Method 1: Use python -m pyinstaller
        print("Attempting to run: python -m pyinstaller")
        try:
            print(f"Running command: {sys.executable} -m PyInstaller --clean ai_assessor.spec")
            result = subprocess.run(
                [sys.executable, "-m", "PyInstaller", "--clean", "ai_assessor.spec"],
                check=False,  # Don't raise exception so we can try other methods
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("PyInstaller completed successfully.")
                pyinstaller_success = True
            else:
                print(f"Failed with return code {result.returncode}")
                print("Output:")
                print(result.stdout)
                print("Error:")
                print(result.stderr)
        except Exception as e:
            print(f"Error running python -m PyInstaller: {e}")
        
        # Method 2: Try using pyinstaller command directly
        if not pyinstaller_success:
            print("\nAttempting to run pyinstaller directly")
            pyinstaller_cmd = shutil.which("pyinstaller")
            if pyinstaller_cmd:
                try:
                    print(f"Running command: {pyinstaller_cmd} --clean ai_assessor.spec")
                    result = subprocess.run(
                        [pyinstaller_cmd, "--clean", "ai_assessor.spec"],
                        check=False,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("PyInstaller completed successfully.")
                        pyinstaller_success = True
                    else:
                        print(f"Failed with return code {result.returncode}")
                        print("Output:")
                        print(result.stdout)
                        print("Error:")
                        print(result.stderr)
                except Exception as e:
                    print(f"Error running pyinstaller command: {e}")
            else:
                print("PyInstaller command not found in PATH.")
        
        # Method 3: Try using Scripts\pyinstaller.exe (for Windows)
        if not pyinstaller_success and sys.platform.startswith('win'):
            print("\nAttempting to run PyInstaller from Scripts directory")
            scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
            pyinstaller_exe = os.path.join(scripts_dir, "pyinstaller.exe")
            
            if os.path.exists(pyinstaller_exe):
                try:
                    print(f"Running command: {pyinstaller_exe} --clean ai_assessor.spec")
                    result = subprocess.run(
                        [pyinstaller_exe, "--clean", "ai_assessor.spec"],
                        check=False,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print("PyInstaller completed successfully.")
                        pyinstaller_success = True
                    else:
                        print(f"Failed with return code {result.returncode}")
                        print("Output:")
                        print(result.stdout)
                        print("Error:")
                        print(result.stderr)
                except Exception as e:
                    print(f"Error running PyInstaller from Scripts: {e}")
            else:
                print(f"PyInstaller not found at {pyinstaller_exe}")
        
        if not pyinstaller_success:
            print("\nAll PyInstaller execution methods failed.")
            print("Please try manually running: python -m PyInstaller --clean ai_assessor.spec")
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