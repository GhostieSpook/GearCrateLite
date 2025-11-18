@echo off
echo ====================================
echo Manueller Import aus Textdatei
echo ====================================
echo.
echo Importiert Items aus items_to_import.txt
echo.
echo Bearbeite die Datei zuerst und fuege
echo deine Item-Namen ein (eine pro Zeile).
echo.
pause

python src/import_from_file.py
