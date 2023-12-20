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

echo Found Python 3.10 installation....

:: Create virtual environment if it doesn't exist
if not exist qtquickdetect_runtime_cuda (
    echo Creating runtime environment...

    python3.10 -m venv qtquickdetect_runtime_cuda
    if %errorlevel% NEQ 0 (
        echo Failed to create virtual environment.
        exit /b 1
    )

    echo Created runtime environment.
)

:: Activate virtual environment
call qtquickdetect_runtime_cuda/Scripts/activate.bat

:: Install dependencies (Did I mention pip is horrible?)
echo Syncing dependencies...
python -m pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 

echo Everything is ready, running qtquickdetect...

:: Run the script
python qtquickdetect.py 
