@echo off
REM Simple Build Script (No Virtual Environment)
REM Use this if you already have all dependencies installed globally

echo ============================================================
echo Building System Monitor Executable (Simple Mode)
echo ============================================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt

REM Verify PyInstaller installation
echo Verifying PyInstaller installation...
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

REM Build executable
echo Building executable with PyInstaller...
python -m PyInstaller system_monitor.spec

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Build failed!
    echo ============================================================
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo   - Missing dependencies: Run "python -m pip install -r requirements.txt"
    echo   - Antivirus interference: Temporarily disable antivirus
    echo   - Disk space: Ensure you have at least 500MB free space
    echo.
    pause
    exit /b 1
)

REM Create data directory in dist
echo Creating data directory...
if not exist "dist\SystemMonitor\data\" mkdir dist\SystemMonitor\data

REM Copy README
echo Copying README...
copy README.md dist\SystemMonitor\ >nul 2>&1

REM Copy launcher
echo Copying launcher...
copy START_MONITOR.bat dist\SystemMonitor\ >nul 2>&1

echo.
echo ============================================================
echo Build Complete!
echo ============================================================
echo.
echo Executable location: dist\SystemMonitor\SystemMonitor.exe
echo.
echo To run the application:
echo   1. Navigate to dist\SystemMonitor\
echo   2. Double-click SystemMonitor.exe or START_MONITOR.bat
echo   3. Open browser to http://localhost:5000
echo.
echo To distribute:
echo   1. Zip the entire dist\SystemMonitor\ folder
echo   2. Send the zip file to users
echo   3. Users extract and run SystemMonitor.exe
echo.
pause
