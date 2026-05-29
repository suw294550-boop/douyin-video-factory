@echo off
title Publish Videos
echo ========================================
echo   Publish Videos
echo ========================================
echo   Publishing latest batch...
echo.
python "%~dp0..\run.py" publish --latest
pause
