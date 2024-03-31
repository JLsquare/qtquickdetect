#!/bin/bash

echo "
░██████╗░████████╗░██████╗░██╗░░░██╗██╗░█████╗░██╗░░██╗██████╗░███████╗████████╗███████╗░█████╗░████████╗
██╔═══██╗╚══██╔══╝██╔═══██╗██║░░░██║██║██╔══██╗██║░██╔╝██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗╚══██╔══╝
██║██╗██║░░░██║░░░██║██╗██║██║░░░██║██║██║░░╚═╝█████═╝░██║░░██║█████╗░░░░░██║░░░█████╗░░██║░░╚═╝░░░██║░░░
╚██████╔╝░░░██║░░░╚██████╔╝██║░░░██║██║██║░░██╗██╔═██╗░██║░░██║██╔══╝░░░░░██║░░░██╔══╝░░██║░░██╗░░░██║░░░
░╚═██╔═╝░░░░██║░░░░╚═██╔═╝░╚██████╔╝██║╚█████╔╝██║░╚██╗██████╔╝███████╗░░░██║░░░███████╗╚█████╔╝░░░██║░░░
░░░╚═╝░░░░░░╚═╝░░░░░░╚═╝░░░░╚═════╝░╚═╝░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝░░░╚═╝░░░╚══════╝░╚════╝░░░░╚═╝░░░
"

echo "Checking for virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment found."
    source venv/bin/activate
else
    echo "Virtual environment not found."
    echo "Setting up environment..."

    echo "Do you want to install with CUDA support? (y/n)"
    read cuda
    while [[ "$cuda" != "y" && "$cuda" != "n" ]]; do
        echo "Please answer 'y' for yes or 'n' for no."
        read cuda
    done

    echo "Creating virtual environment..."
    python -m venv venv
    echo "Virtual environment created."

    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Virtual environment activated."

    echo "Installing requirements..."
    if [ "$cuda" = "y" ]; then
        echo "Installing PyTorch with CUDA support..."
        pip install torch torchvision
    else
        echo "Installing PyTorch without CUDA support..."
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    fi
    echo "PyTorch installed successfully."
    echo "Installing other requirements..."
    pip install -r requirements.txt
    echo "Requirements installed successfully."

    echo "Setup complete."
fi

echo "Running qtquickdetect.py..."
python qtquickdetect.py

echo "Execution complete."
echo "Press any key to close this window."
read -n 1 -s -r
