# Windows Distribution Guide

This document explains how to build and distribute the AI Assessor application for Windows users.

## Building the Windows Executable

### Easy Method (Recommended)

1. **Setup Windows Environment**
   - You need a Windows machine with Python 3.8 or higher installed
   - Clone or download this repository to the Windows machine

2. **Run the Setup Batch File**
   - Double-click on `setup_build_windows.bat` or run it from Command Prompt
   - This script will:
     - Create a virtual environment
     - Install all required packages including PyInstaller
     - Guide you through the build process

3. **Building**
   - The batch file will offer to run the build script automatically
   - If you choose not to run it immediately, you can run it later with:
     ```
     venv\Scripts\activate
     python build_windows.py
     ```

### Manual Method

If you prefer to do the setup manually:

1. **Create and Activate a Virtual Environment**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install Requirements**
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Run the Build Script**
   ```
   python build_windows.py
   ```

4. **The Build Process**
   - PyInstaller will package the application into a standalone executable
   - The script will create a complete distribution folder in `dist/AI_Assessor/`
   - This folder contains the executable and all necessary files

## Distribution Structure

The distribution folder contains:

```
AI_Assessor/
├── AI_Assessor.exe      # Main executable
├── config.ini           # Pre-configured settings
├── README.txt           # Instructions for users
├── run_ai_assessor.bat  # Batch file to run the app
├── prompts/            
│   ├── system_prompt.txt
│   ├── user_prompt.txt
│   ├── example_system_prompt.txt
│   └── example_user_prompt.txt
├── submissions/         # Sample submissions
│   └── *.docx
├── support/             # Rubrics and guidelines
│   └── *.docx
└── output/              # For assessment results
```

## Distributing to Users

1. **Package the Application**
   - Zip the entire `dist/AI_Assessor/` folder
   - Name it something like `AI_Assessor_Windows_vX.X.zip`

2. **User Instructions**
   - Users should extract the entire zip file to a location on their computer
   - They can run the application by double-clicking `AI_Assessor.exe` or using the batch file
   - No Python installation is required
   - Users need to enter their OpenAI API key in the Settings tab
   - The README.txt file provides basic usage instructions

3. **Folder Usage**
   - Users can place their student submissions in the `submissions` folder
   - Assessment results will be saved in the `output` folder
   - The `support` folder contains rubrics and guidelines
   - Users can edit the prompt files in the `prompts` folder

## Troubleshooting

Common issues users might encounter:

1. **Missing DLLs**: If users get DLL errors, they might need to install the Microsoft Visual C++ Redistributable
2. **API Key Issues**: Make sure users understand they need their own OpenAI API key
3. **Antivirus Alerts**: Some antivirus software might flag PyInstaller-packaged apps; you may need to create an exception

## Updating the Application

When updating the application:

1. Increment the version number in any version-specific files
2. Make sure to test the package thoroughly before distribution
3. Provide clear update instructions to users