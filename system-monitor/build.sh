#!/bin/bash
# Linux/Mac Build Script for System Monitor

echo "============================================================"
echo "Building System Monitor Executable"
echo "============================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Verify PyInstaller installation
echo "Verifying PyInstaller installation..."
if ! python3 -m pip show pyinstaller > /dev/null 2>&1; then
    echo "ERROR: PyInstaller is not installed!"
    echo "Installing PyInstaller..."
    python3 -m pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build executable
echo "Building executable with PyInstaller..."
python3 -m PyInstaller system_monitor.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "============================================================"
    echo "ERROR: Build failed!"
    echo "============================================================"
    echo "Please check the error messages above."
    echo ""
    exit 1
fi

# Create data directory in dist
echo "Creating data directory..."
mkdir -p dist/SystemMonitor/data

# Copy README
echo "Copying README..."
cp README.md dist/SystemMonitor/

# Make executable runnable
chmod +x dist/SystemMonitor/SystemMonitor

echo "============================================================"
echo "Build Complete!"
echo "============================================================"
echo ""
echo "Executable location: dist/SystemMonitor/SystemMonitor"
echo ""
echo "To run the application:"
echo "  1. Navigate to dist/SystemMonitor/"
echo "  2. Run ./SystemMonitor"
echo "  3. Open browser to http://localhost:5000"
echo ""
