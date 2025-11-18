@echo off
echo ====================================
echo SC Inventory Manager wird gestartet...
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    echo Bitte installiere Python von https://www.python.org/
    pause
    exit /b 1
)

REM Start the application
python src/main.py

REM If there's an error, keep window open
if errorlevel 1 (
    echo.
    echo ====================================
    echo FEHLER beim Starten!
    echo ====================================
    echo.
    echo Falls du das Programm zum ersten Mal startest,
    echo fuehre bitte zuerst install.bat aus!
    echo.
    pause
)
