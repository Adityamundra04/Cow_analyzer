@echo off
echo ========================================
echo Cow Farm Analytics - Easy Setup
echo ========================================
echo.

REM Check if venv exists
if exist venv (
    echo Virtual environment found. Activating...
    call venv\Scripts\activate
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        echo Please make sure Python is installed and added to PATH.
        pause
        exit /b 1
    )
    call venv\Scripts\activate
    
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Starting Cow Farm Analytics App...
echo ========================================
echo.
echo The app will open in your browser at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause
