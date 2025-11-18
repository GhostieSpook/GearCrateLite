@echo off
echo ====================================
echo SC Inventory Manager - Setup
echo ====================================
echo.
echo Dieses Script wird:
echo 1. Dependencies installieren
echo 2. Das Programm starten
echo.
pause

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    echo Bitte installiere Python von https://www.python.org/
    pause
    exit /b 1
)

echo.
echo [1/2] Installiere Dependencies...
echo ====================================
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
echo [2/2] Starte Programm...
echo ====================================
echo.

REM Start the application
python src/main.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo FEHLER beim Starten!
    echo ====================================
    echo.
    pause
)
