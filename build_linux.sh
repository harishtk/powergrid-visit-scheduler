#!/bin/bash
# ─────────────────────────────────────────────
#  Build Linux executable with PyInstaller
# ─────────────────────────────────────────────

VENV_DIR=".venv"
MAIN_SCRIPT="gui_app.py"
APP_NAME="PowerGridScheduler"
DATA_SCRIPT="powergrid_visit_scheduler.py"

echo "=== Building $APP_NAME for Linux ==="

# 1. Activate venv
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "ERROR: Virtual environment not found at $VENV_DIR."
    echo "Please create it first: python3 -m venv $VENV_DIR"
    exit 1
fi

# 2. Ensure PyInstaller is installed
if ! pip show pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller -q
fi

# 3. Build
echo "Running PyInstaller..."
pyinstaller --noconfirm --onefile --windowed \
    --name "$APP_NAME" \
    --add-data "$DATA_SCRIPT:." \
    "$MAIN_SCRIPT"

if [ $? -ne 0 ]; then
    echo "BUILD FAILED!"
    exit 1
fi

echo ""
echo "=== Build complete! ==="
echo "Executable: dist/$APP_NAME"
echo ""
