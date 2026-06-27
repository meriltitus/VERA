@echo off
title VERA
color 0A

:: Navigate to vera folder
cd /d "%~dp0vera"

:: Check if venv exists
if not exist .venv (
    echo  [ERROR] VERA is not installed yet.
    echo  Please run "Install VERA.bat" first.
    echo.
    pause
    exit /b 1
)

:: Check if Ollama is running, start it if not
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if %errorlevel% neq 0 (
    echo  Starting AI engine...
    start /min "" ollama serve
    timeout /t 3 /nobreak >nul
)

:: Activate venv and start VERA
call .venv\Scripts\activate.bat

echo.
echo  ============================================
echo   VERA is starting...
echo   Your browser will open automatically.
echo   Keep this window open while using VERA.
echo   Close this window to shut VERA down.
echo  ============================================
echo.

:: Open browser after short delay
start "" timeout /t 4 /nobreak >nul & start "" "http://localhost:8501"

:: Start Streamlit
streamlit run ui/app.py --server.headless true --browser.gatherUsageStats false
