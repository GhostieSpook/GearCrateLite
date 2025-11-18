@echo off
echo ====================================
echo CStone.space Quick Import
echo ====================================
echo.
echo Dieser Import ist SCHNELLER, weil
echo nur die Item-Namen importiert werden.
echo.
echo Bilder koennen spaeter ueber die
echo normale Suche hinzugefuegt werden.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    pause
    exit /b 1
)

echo Starte Quick Import...
echo.

REM Run the quick importer
python src/quick_import.py

echo.
pause
