@echo off
echo ====================================
echo GearCrate - Desktop Mode
echo ====================================
echo.
echo Dieser Modus startet GearCrate als
echo Desktop-Anwendung mit pywebview.
echo.
echo Features:
echo - HTTP Server im Hintergrund
echo - Desktop-Fenster
echo - Bereit fuer Auto-Import
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    pause
    exit /b 1
)

echo Starte GearCrate Desktop...
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
