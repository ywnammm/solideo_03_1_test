@echo off
REM Windows Build Script for System Monitor

echo ============================================================
echo Building System Monitor Executable
echo ============================================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

REM Build executable
echo Building executable with PyInstaller...
pyinstaller system_monitor.spec

REM Create data directory in dist
echo Creating data directory...
if not exist "dist\SystemMonitor\data\" mkdir dist\SystemMonitor\data

REM Copy README
echo Copying README...
copy README.md dist\SystemMonitor\

echo ============================================================
echo Build Complete!
echo ============================================================
echo.
echo Executable location: dist\SystemMonitor\SystemMonitor.exe
echo.
echo To run the application:
echo   1. Navigate to dist\SystemMonitor\
echo   2. Run SystemMonitor.exe
echo   3. Open browser to http://localhost:5000
echo.
pause
