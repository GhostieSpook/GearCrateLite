@echo off
echo ====================================
echo SC Items Starter-Pack Import
echo ====================================
echo.
echo Importiert die vorgefertigte Liste mit
echo 50+ Star Citizen Armor Items!
echo.

REM Copy if needed
if not exist items.csv (
    echo Kopiere star_citizen_items.csv zu items.csv...
    copy star_citizen_items.csv items.csv >nul
)

python src/import_csv.py

echo.
echo Du kannst jetzt weitere Items hinzufuegen,
echo indem du items.csv bearbeitest!
echo.
pause
