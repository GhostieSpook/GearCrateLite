@echo off
REM ====================================
REM GearCrate - Desktop Mode (ADMIN)
REM ====================================
REM This script requests administrator privileges
REM Required for InvDetect scanner functionality

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    REM Already running as admin, start GearCrate
    goto :run_gearcrate
) else (
    REM Not admin, request elevation
    echo Requesting administrator privileges...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:run_gearcrate
REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo ====================================
echo GearCrate - Desktop Mode (ADMIN)
echo ====================================
echo.
echo Dieser Modus startet GearCrate als
echo Desktop-Anwendung mit Admin-Rechten.
echo.
echo Features:
echo - HTTP Server im Hintergrund
echo - Desktop-Fenster
echo - InvDetect Scanner mit vollen Rechten
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    pause
    exit /b 1
)

echo Starte GearCrate Desktop (Admin)...
echo Working Directory: %CD%
echo.

REM Start the desktop version
python src/main_desktop.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo FEHLER beim Starten!
    echo ====================================
    echo.
    echo Moegliche Ursachen:
    echo - pywebview nicht installiert
    echo - Port 8080 bereits belegt
    echo.
    pause
)
