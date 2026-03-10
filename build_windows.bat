@echo off
REM ─────────────────────────────────────────────
REM  Build Windows executable with PyInstaller
REM ─────────────────────────────────────────────
setlocal

set VENV_DIR=.venv
set MAIN_SCRIPT=gui_app.py
set APP_NAME=PowerGridScheduler
set DATA_SCRIPT=powergrid_visit_scheduler.py

echo === Building %APP_NAME% for Windows ===

REM 1. Activate venv
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo ERROR: Virtual environment not found at %VENV_DIR%.
    echo Please create it first: python -m venv %VENV_DIR%
    exit /b 1
)

REM 2. Ensure PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller -q
)

REM 3. Build
echo Running PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --name "%APP_NAME%" ^
    --add-data "%DATA_SCRIPT%;." ^
    "%MAIN_SCRIPT%"

if errorlevel 1 (
    echo BUILD FAILED!
    exit /b 1
)

echo.
echo === Build complete! ===
echo Executable: dist\%APP_NAME%.exe
echo.

endlocal
