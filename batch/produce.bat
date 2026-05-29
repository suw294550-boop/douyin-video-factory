@echo off
title Produce Videos
echo ========================================
echo   Produce Videos
echo ========================================
echo.
echo  [1] Emotional x10
echo  [2] Cold Knowledge x10
echo  [3] Motivation x10
echo  [4] All topics x5 each
echo.
set /p choice="  Choice (1-4): "

if "%choice%"=="1" python "%~dp0..\run.py" produce --topic emotional --count 10
if "%choice%"=="2" python "%~dp0..\run.py" produce --topic cold_knowledge --count 10
if "%choice%"=="3" python "%~dp0..\run.py" produce --topic motivation --count 10
if "%choice%"=="4" python "%~dp0..\run.py" produce --all
pause
