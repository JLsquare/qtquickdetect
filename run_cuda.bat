@echo off

:: Make sure we're within the qtquickdetect directory
if not exist requirements.txt (
    echo Please run this script from the qtquickdetect directory.
    exit /b 1
)

:: Check for an existing python 3.10 installation
where python3.10 >nul 2>nul
if %errorlevel% NEQ 0 (
    echo Python 3.10 not found. Please refer to the README.md file for instructions on how to install it.
    exit /b 1
)

echo Found Python 3.10 installation, creating runtime environment...

:: Create virtual environment if it doesn't exist
if not exist qtquickdetect_runtime (
    python3.10 -m venv qtquickdetect_runtime
    if %errorlevel% NEQ 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )
)

:: Activate virtual environment
call qtquickdetect_runtime/Scripts/activate.bat

echo Created runtime environment, installing dependencies...

:: Install dependencies
python -m pip install -Ur requirements_cuda.txt

echo Everything is ready, running qtquickdetect...

:: Run the script
python qtquickdetect.py 
