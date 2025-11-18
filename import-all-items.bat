@echo off
echo ====================================
echo CStone.space Bulk Import
echo ====================================
echo.
echo Dieses Script importiert ALLE Items
echo von CStone.space in deine Datenbank.
echo.
echo Das kann mehrere Minuten dauern!
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert!
    pause
    exit /b 1
)

echo Starte Import...
echo.

REM Run the bulk importer
python src/bulk_import.py

echo.
pause
