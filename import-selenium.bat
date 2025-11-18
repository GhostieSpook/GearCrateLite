@echo off
echo ====================================
echo CStone Selenium Import
echo ====================================
echo.
echo Dieser Import nutzt Selenium um
echo die JavaScript-geladenen Items
echo von CStone.space zu holen.
echo.
echo Chrome wird sich oeffnen!
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    pause
    exit /b 1
)

echo Starte Selenium Import...
echo.

python src/selenium_import.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo FEHLER!
    echo ====================================
    echo.
    echo Falls ChromeDriver nicht installiert ist:
    echo 1. Fuehre install-selenium.bat aus
    echo 2. Lade ChromeDriver herunter
    echo 3. Versuche es erneut
    echo.
    pause
)

echo.
echo Fertig!
echo.
pause
