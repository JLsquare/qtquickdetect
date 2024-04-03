@echo off

echo ░██████╗░████████╗░██████╗░██╗░░░██╗██╗░█████╗░██╗░░██╗██████╗░███████╗████████╗███████╗░█████╗░████████╗
echo ██╔═══██╗╚══██╔══╝██╔═══██╗██║░░░██║██║██╔══██╗██║░██╔╝██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝
echo ██║██╗██║░░░██║░░░██║██╗██║██║░░░██║██║██║░░╚═╝█████═╝░██║░░██║█████╗░░░░░██║░░░█████╗░░██║░░╚═╝░░░██║░░░
echo ╚██████╔╝░░░██║░░░╚██████╔╝██║░░░██║██║██║░░██╗██╔═██╗░██║░░██║██╔══╝░░░░░██║░░░██╔══╝░░██║░░██╗░░░██║░░░
echo ░╚═██╔═╝░░░░██║░░░░╚═██╔═╝░╚██████╔╝██║╚█████╔╝██║░╚██╗██████╔╝███████╗░░░██║░░░███████╗╚█████╔╝░░░██║░░░
echo ░░░╚═╝░░░░░░╚═╝░░░░░░╚═╝░░░░╚═════╝░╚═╝░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝░░░╚═╝░░░╚══════╝░╚════╝░░░░╚═╝░░░

echo Checking for virtual environment...
if exist "venv" (
    echo Virtual environment found.
    goto :activateVenv
) else (
    echo Virtual environment not found.
    echo Setting up environment...
    goto :askCuda
)

:askCuda
echo Do you want to install with CUDA support? (y/n)
set /p cuda=
:checkInput
if /I "%cuda%"=="y" (goto :createVenv) else if /I "%cuda%"=="n" (goto :createVenv) else (
    echo Please answer 'y' for yes or 'n' for no.
    set /p cuda=
    goto :checkInput
)

:createVenv
echo Creating virtual environment...
python -m venv venv
echo Virtual environment created.

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.

echo Installing requirements...
if /I "%cuda%"=="y" (
    echo Installing PyTorch with CUDA support...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
) else (
    echo Installing PyTorch without CUDA support...
    pip install torch torchvision
)
echo PyTorch installed successfully.
echo Installing other requirements...
pip install -r requirements.txt
echo Requirements installed successfully.

echo Setup complete.
goto :proceedToExecution

:activateVenv
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.

:proceedToExecution
echo Running qtquickdetect.py...
python qtquickdetect.py
