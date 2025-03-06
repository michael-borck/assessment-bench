@echo off
echo AI Assessor - Windows Build Setup
echo ================================
echo.

REM Display timestamp
echo Setup started at: %date% %time%
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Display Python version
echo Using Python:
python --version
echo.

REM Check if venv already exists
if exist venv\Scripts\activate.bat (
    echo Virtual environment already exists.
) else (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

REM Check if activation was successful
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment. Please check your Python installation.
    exit /b 1
)

REM Check if pip needs upgrading
echo Checking pip version...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo Checking for PyInstaller...
pip show pyinstaller > nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller already installed.
)

echo.
echo --------------------------------------
echo Environment Information:
python -c "import sys; print(f'Python: {sys.version}')"
echo Virtual env: %VIRTUAL_ENV%
echo --------------------------------------
echo.

echo Setup complete! Now you can run the build script.
echo.

REM Ask user if they want to continue with build
set /p run_now=Run the build script now? (y/n): 

if /i "%run_now%"=="y" (
    echo.
    echo Running build script...
    python build_windows.py
    
    REM Check if build was successful
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Build failed. Please check the error messages above.
    ) else (
        echo.
        echo Build completed successfully!
    )
) else (
    echo.
    echo You can run the build script later with these commands:
    echo   call venv\Scripts\activate
    echo   python build_windows.py
)

echo.
echo Setup finished at: %date% %time%
echo.
pause