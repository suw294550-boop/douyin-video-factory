@echo off
title Douyin Video Factory - Installer
echo ========================================
echo   Douyin Video Factory - Installer
echo ========================================
echo.
echo This will install all dependencies.
echo Required: Python 3.10+, ffmpeg, Ollama
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found

:: Check ffmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARN] ffmpeg not found. Video compositing won't work.
    echo Install from: https://ffmpeg.org/download.html
) else (
    echo [OK] ffmpeg found
)

:: Check Ollama
ollama list >nul 2>&1
if errorlevel 1 (
    echo [WARN] Ollama not found. AI generation won't work.
    echo Install from: https://ollama.com/
) else (
    echo [OK] Ollama found
    :: Check model
    ollama list 2>nul | findstr "qwen3" >nul
    if errorlevel 1 (
        echo.
        echo Pulling qwen3:8b model (5.2GB, first time only)...
        ollama pull qwen3:8b
    ) else (
        echo [OK] Model qwen3:8b found
    )
)

:: Install Python packages
echo.
echo Installing Python packages...
pip install -r "%~dp0requirements.txt" -q
echo [OK] Python packages

:: Install Playwright browser
echo.
echo Installing Playwright browser...
python -m playwright install chromium
echo [OK] Playwright

:: Generate BGM
echo.
echo Generating BGM library...
python "%~dp0scripts\generate_bgm.py"

:: Create desktop shortcut
echo.
echo Creating desktop shortcut...
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\DouyinFactory.lnk');$s.TargetPath='C:\Python311\python.exe';$s.Arguments='\"%~dp0run.py\" ui';$s.WorkingDirectory='%~dp0';$s.IconLocation='shell32.dll,15';$s.Save()"
echo [OK] Desktop shortcut

echo.
echo ========================================
echo   Installation Complete!
echo   Double-click "DouyinFactory" on your desktop
echo   Or run: python run.py ui
echo.
echo   First time: go to Settings - click login
echo ========================================
pause
