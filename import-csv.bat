@echo off
echo ====================================
echo CSV Import
echo ====================================
echo.
echo Importiert Items aus einer CSV-Datei
echo.
echo Verfuegbare Dateien:
echo - items.csv (deine eigene Liste)
echo - star_citizen_items.csv (vorgefertigte Liste)
echo.

python src/import_csv.py

pause
