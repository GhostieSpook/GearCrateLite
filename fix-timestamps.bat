@echo off
echo ========================================
echo GearCrate - Timestamp Migration
echo ========================================
echo.
echo Dieses Script fuegt das 'created_at' Feld
echo zu deinen bestehenden Items hinzu.
echo.
echo Die Timestamps werden geschaetzt basierend
echo auf der Reihenfolge der IDs.
echo (ID 1 = aeltestes Item, etc.)
echo.
pause
echo.

python migrate_timestamps.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo FEHLER beim Ausfuehren!
    echo ====================================
    pause
    exit /b 1
)

echo.
echo ====================================
echo ERFOLGREICH!
echo ====================================
echo.
echo Du kannst jetzt GearCrate starten und
echo nach "Zuletzt hinzugefuegt" sortieren!
echo.
pause
