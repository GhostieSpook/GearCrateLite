@echo off
echo ====================================
echo SC Inventory Manager - Cleanup
echo ====================================
echo.
echo WARNUNG: Dieser Vorgang loescht:
echo - Die Datenbank (alle deine Items!)
echo - Den Bild-Cache
echo.
echo Die Programm-Dateien bleiben erhalten.
echo.
set /p confirm="Wirklich fortfahren? (J/N): "

if /i not "%confirm%"=="J" (
    echo Abgebrochen.
    pause
    exit /b 0
)

echo.
echo Loesche Datenbank und Cache...

REM Delete database
if exist "data\inventory.db" (
    del /f /q "data\inventory.db"
    echo - Datenbank geloescht
)

if exist "data\inventory.db-journal" (
    del /f /q "data\inventory.db-journal"
)

REM Delete cache
if exist "data\cache\images\*" (
    del /f /q "data\cache\images\*"
    echo - Cache geleert
)

echo.
echo ====================================
echo Cleanup abgeschlossen!
echo ====================================
echo.
pause
