@echo off
title Douyin Factory Setup
echo ========================================
echo   Douyin Video Factory - Setup
echo ========================================
echo.
echo [1/4] Installing Python packages...
pip install -r "%~dp0..\requirements.txt" -q
echo   Done.
echo.
echo [2/4] Installing Playwright browser...
python -m playwright install chromium
echo   Done.
echo.
echo [3/4] Checking Ollama...
ollama list 2>nul | findstr "qwen" >nul
if errorlevel 1 (
    echo   Pulling qwen3:8b (5.2GB, first time only)...
    ollama pull qwen3:8b
) else (
    echo   Ollama model found.
)
echo.
echo [4/4] Generating BGM library...
python "%~dp0..\scripts\generate_bgm.py"
echo.
echo ========================================
echo   Setup Complete!
echo   Next: run login.bat to scan QR code
echo ========================================
pause
