@echo off
title VERA Installer
color 0A
echo.
echo  ============================================
echo   VERA - Verifiable Evidence ^& Reasoning
echo   First-Time Setup
echo  ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python is not installed on this computer.
    echo.
    echo  Please install Python 3.10 or higher from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During installation, check the box that says
    echo  "Add Python to PATH" before clicking Install.
    echo.
    pause
    exit /b 1
)

echo  [OK] Python found.
echo.

:: Check if Ollama is installed
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ACTION REQUIRED] Ollama is not installed.
    echo.
    echo  Ollama is the AI engine that powers VERA.
    echo  Opening the download page in your browser now...
    echo.
    start https://ollama.com/download
    echo  Please:
    echo  1. Download and install Ollama
    echo  2. Once installed, close this window
    echo  3. Run "Install VERA.bat" again
    echo.
    pause
    exit /b 1
)

echo  [OK] Ollama found.
echo.

:: Navigate to project root folder
cd /d "%~dp0"

:: Create virtual environment
echo  Setting up Python environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo  [ERROR] Could not create virtual environment.
    pause
    exit /b 1
)
echo  [OK] Environment created.
echo.

:: Install dependencies
echo  Installing dependencies (this may take a few minutes)...
call .venv\Scripts\activate.bat
.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
echo  [OK] Dependencies installed.
echo.

:: Pull AI models
echo  Downloading AI models (this may take 10-15 minutes)...
echo  Downloading Llama 3 (4.7GB)...
ollama pull llama3
echo  Downloading embedding model...
ollama pull nomic-embed-text
echo  [OK] AI models ready.
echo.

:: Create .env file if it doesn't exist
if not exist .env (
    copy .env.example .env >nul
    echo  [OK] Config file created.
)

:: Create data folders
if not exist data\vectorstore mkdir data\vectorstore
if not exist data\raw mkdir data\raw

echo.
echo  ============================================
echo   Installation complete!
echo   Double-click "Start VERA.bat" to launch.
echo  ============================================
echo.
pause
