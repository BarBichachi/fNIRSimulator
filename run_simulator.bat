@echo off
REM Launches the fNIRS Simulator using its own virtual environment.
setlocal
cd /d "%~dp0"

set "VENV_PY=.venv\Scripts\python.exe"

if exist "%VENV_PY%" goto run

echo [run_simulator] No virtual environment found. Creating one...
py -3.12 -m venv .venv 2>nul
if not exist "%VENV_PY%" python -m venv .venv
if not exist "%VENV_PY%" goto novenv

echo [run_simulator] Installing dependencies: PySide6 pylsl numpy
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install PySide6 pylsl numpy
if errorlevel 1 goto pipfail

:run
echo [run_simulator] Launching fNIRS Simulator...
"%VENV_PY%" main.py
if errorlevel 1 pause
exit /b 0

:novenv
echo [run_simulator] ERROR: could not create a virtual environment.
echo [run_simulator] Install Python 3.12 from python.org and try again.
pause
exit /b 1

:pipfail
echo [run_simulator] ERROR: dependency installation failed.
pause
exit /b 1
