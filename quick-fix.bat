@echo off
echo ========================================
echo GearCrate - Quick Fix
echo ========================================
echo.
echo Fixe:
echo 1. Bilder werden nicht angezeigt
echo 2. Modal laesst sich nicht schliessen
echo.

echo [1/2] Aktualisiere JavaScript...
copy "web\app_buttons.js" "web\app.js" /Y >nul
if errorlevel 1 (
    echo FEHLER beim Kopieren!
    pause
    exit /b 1
)
echo       JavaScript aktualisiert

echo.
echo [2/2] Server bereits aktualisiert (main_browser.py)
echo       Cache-Image-Serving aktiviert

echo.
echo ========================================
echo FIX ABGESCHLOSSEN!
echo ========================================
echo.
echo Die Fixes sind installiert:
echo - Bilder werden jetzt richtig serviert
echo - Modal kann geschlossen werden
echo.
echo WICHTIG: Server neu starten!
echo.
echo 1. Druecke Strg+C in der Server-Konsole
echo 2. Starte neu: start-browser.bat
echo 3. Hard-Refresh im Browser: Strg+Shift+R
echo.
pause
