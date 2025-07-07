@echo off
echo.
echo 🛠️ Yellow Haven Lodge - Invoice Generator Builder
echo ==================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/ 
    pause
    exit /b
)

:: Clean up previous builds
if exist "build" (
    echo 🔥 Removing old build folder...
    rmdir /s /q build
)

if exist "dist" (
    echo 🗑️ Removing old dist folder...
    rmdir /s /q dist
)

if exist "*.spec" (
    echo 🗑️ Removing old .spec file...
    del *.spec
)

:: Build new executable
echo 🧱 Building new executable...
python -m PyInstaller --onefile --windowed invoice_generator.py

:: Done
echo.
echo ✅ Build complete!
echo Your standalone app is in the 'dist' folder: dist\invoice_generator.exe
echo.

pause