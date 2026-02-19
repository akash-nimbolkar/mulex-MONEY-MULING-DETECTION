@echo off
REM Quick Setup Script for Money Muling Detection Engine - Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Money Muling Detection Engine - Setup
echo RIFT 2026 Hackathon Challenge
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Installing Backend Dependencies...
cd backend
call pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo [✓] Backend dependencies installed

echo.
echo [2/4] Generating Sample Test Data...
python sample_csv_generator.py

if errorlevel 1 (
    echo WARNING: Failed to generate sample data
) else (
    echo [✓] Sample data generated (sample_transactions.csv)
)

cd ..

echo.
echo [3/4] Installing Frontend Dependencies...
cd frontend
call npm install

if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo [✓] Frontend dependencies installed

cd ..

echo.
echo [4/4] Verification...
python --version
echo [✓] Python ready
node --version
echo [✓] Node.js ready
npm --version
echo [✓] npm ready

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Start Backend:
echo    cd backend ^&^& python app.py
echo.
echo 2. Start Frontend (in another terminal):
echo    cd frontend ^&^& npm run dev
echo.
echo 3. Open http://localhost:5173 in your browser
echo.
echo 4. Upload sample_transactions.csv from backend/ folder
echo.
echo Documentation: See PROJECT_README.md for detailed info
echo.
pause
