#!/bin/bash

# Configuration
VENV_DIR=".venv"
REQ_FILE="requirements.txt"
MAIN_SCRIPT="gui_app.py"

echo "Setting up PowerGrid Visit Scheduler..."

# 1. Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi

# 2. Check if the python3 venv module is available
if ! python3 -m venv -h &> /dev/null
then
    echo "Error: Python 3 venv module is not installed."
    echo "To fix on Ubuntu/Debian, try running: sudo apt install python3-venv"
    exit 1
fi

# 3. Check if Tkinter is available (required for the GUI)
if ! python3 -c "import tkinter" &> /dev/null
then
    echo "Error: Python Tkinter module is not installed."
    echo "To fix on Ubuntu/Debian, try running: sudo apt install python3-tk"
    exit 1
fi

# 4. Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# 5. Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 6. Install dependencies
echo "Upgrading pip..."
pip install --upgrade pip -q

if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies from $REQ_FILE..."
    pip install -r "$REQ_FILE" -q
else
    echo "No $REQ_FILE found. Proceeding with default installations..."
    pip install python-dateutil six -q
fi

# 7. Run the application
echo "Starting the application..."
python "$MAIN_SCRIPT"

# 8. Deactivate virtual environment when the application is closed
deactivate
echo "Application closed. Virtual environment deactivated."
