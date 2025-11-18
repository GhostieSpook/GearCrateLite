@echo off
echo ========================================
echo GearCrate - Server auf Port 8080 beenden
echo ========================================
echo.

echo Suche Prozess auf Port 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    set PID=%%a
)

if not defined PID (
    echo Kein Server auf Port 8080 gefunden.
    echo.
    pause
    exit /b 0
)

echo Gefundener Prozess: PID %PID%
echo.
echo Beende Prozess...
taskkill /F /PID %PID%

if errorlevel 1 (
    echo FEHLER beim Beenden!
    echo.
    echo Versuche als Administrator:
    echo 1. Rechtsklick auf diese .bat Datei
    echo 2. "Als Administrator ausfuehren"
) else (
    echo.
    echo ✓ Server erfolgreich beendet!
    echo.
    echo Der Import wurde abgebrochen.
    echo Du kannst GearCrate jetzt neu starten.
)

echo.
pause
