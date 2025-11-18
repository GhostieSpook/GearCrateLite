@echo off
echo ======================================
echo Thumbnail Generator
echo ======================================
echo.
echo Generiere Thumbnails fuer vorhandene Bilder...
echo.

cd /d "%~dp0"
python generate_thumbnails.py

echo.
echo Fertig!
pause
