@echo off
echo ====================================
echo SC Inventory Manager (Browser-Modus)
echo ====================================
echo.
echo Dieser Modus startet einen lokalen
echo Server und oeffnet dein Browser.
echo.
echo Das ist eine Alternative falls
echo pywebview Probleme macht.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    pause
    exit /b 1
)

echo Starte Server...
echo.

REM Start the browser version
python src/main_browser.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo FEHLER beim Starten!
    echo ====================================
    echo.
    pause
)
