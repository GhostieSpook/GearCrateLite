@echo off
echo ====================================
echo SC Inventory Manager - Installation
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

echo Python gefunden. Installiere Dependencies...
echo.

REM Install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Installation fehlgeschlagen. Versuche mit --break-system-packages...
    pip install -r requirements.txt --break-system-packages
)

echo.
echo ====================================
echo Installation abgeschlossen!
echo ====================================
echo.
echo Du kannst das Programm jetzt mit start.bat starten.
echo.
pause
