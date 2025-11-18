@echo off
echo ====================================
echo SC Inventory Manager - Windows Setup
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

echo [1/3] Installiere Basis-Dependencies...
echo ====================================
echo.

REM Install base requirements
python -m pip install --upgrade pip
pip install requests beautifulsoup4 Pillow

echo.
echo [2/3] Installiere pywebview (kann einen Moment dauern)...
echo ====================================
echo.

REM Try to install pywebview with pythonnet
pip install pywebview

if errorlevel 1 (
    echo.
    echo WARNUNG: pywebview Installation fehlgeschlagen!
    echo Das ist normal auf Python 3.14. Installiere alternative Version...
    echo.
    
    REM Install without pythonnet dependency
    pip install --no-deps pywebview
    pip install proxy_tools bottle typing_extensions
)

echo.
echo [3/3] Teste Installation...
echo ====================================
python -c "import requests, bs4, PIL; print('✓ Alle Basis-Module installiert')"

echo.
echo ====================================
echo Installation abgeschlossen!
echo ====================================
echo.
echo Starte das Programm mit start.bat
echo.
pause
