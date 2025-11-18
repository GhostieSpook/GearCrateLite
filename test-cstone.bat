@echo off
echo ====================================
echo CStone Test Scraper
echo ====================================
echo.
echo Analysiert die HTML-Struktur von
echo CStone.space um zu sehen warum
echo keine Items gefunden werden.
echo.

python src/test_scraper.py

echo.
echo Die HTML-Datei wurde gespeichert.
echo Oeffne cstone_debug.html im Browser
echo um die Struktur zu sehen.
echo.
pause
