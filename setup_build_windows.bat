@echo off
echo AI Assessor - Windows Build Setup
echo ================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing requirements...
pip install -r requirements.txt

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Setup complete! Now run the build script:
echo.
echo python build_windows.py
echo.
echo You can run this build script later by:
echo 1. Activating the virtual environment: venv\Scripts\activate
echo 2. Running the build script: python build_windows.py
echo.

set /p run_now=Run the build script now? (y/n): 

if /i "%run_now%"=="y" (
    echo.
    echo Running build script...
    python build_windows.py
) else (
    echo.
    echo You can run the build script later with:
    echo call venv\Scripts\activate
    echo python build_windows.py
)

pause