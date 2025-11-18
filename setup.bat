@echo off
setlocal EnableDelayedExpansion
title GearCrate Setup & Start

echo ===================================================
echo   GearCrate - Automatisches Setup
echo ===================================================
echo.

:: ---------------------------------------------------
:: 1. PRÜFUNG: Ist Python installiert und aktuell genug?
:: ---------------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    goto :INSTALL_PYTHON
)

:: Prüfen ob Version >= 3.8 ist (über ein kleines Inline-Python-Skript)
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"
if %errorlevel% neq 0 (
    echo [!] Deine Python-Version ist zu alt.
    goto :INSTALL_PYTHON
)

echo [OK] Passende Python-Version gefunden.
goto :INSTALL_REQS

:: ---------------------------------------------------
:: 2. PYTHON INSTALLATION (falls nötig)
:: ---------------------------------------------------
:INSTALL_PYTHON
echo.
echo [!] Python wurde nicht gefunden oder ist veraltet.
echo [+] Lade Python 3.11 Installer herunter... (bitte warten)

:: Temporären Ordner nutzen
set "INSTALLER_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
set "INSTALLER_PATH=%TEMP%\python_installer.exe"

:: Download via PowerShell
powershell -Command "Invoke-WebRequest -Uri '!INSTALLER_URL!' -OutFile '!INSTALLER_PATH!'"

if not exist "!INSTALLER_PATH!" (
    echo [FEHLER] Download fehlgeschlagen. Bitte installiere Python manuell von python.org.
    pause
    exit /b
)

echo [+] Installiere Python... (Ein Admin-Fenster oeffnet sich evtl.)
echo     Bitte kurz warten, dies geschieht im Hintergrund.

:: Silent Install mit PATH Variable
start /wait "" "!INSTALLER_PATH!" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo.
echo [!] Python wurde installiert. 
echo [WICHTIG] Damit die Aenderungen wirksam werden, muss das Skript neu starten.
echo.
del "!INSTALLER_PATH!"
pause
:: Startet das Skript neu, damit die neuen Umgebungsvariablen (PATH) geladen werden
start "" "%~f0"
exit

:: ---------------------------------------------------
:: 3. REQUIREMENTS INSTALLIEREN
:: ---------------------------------------------------
:INSTALL_REQS
echo.
echo [+] Prüfe und installiere Requirements (requirements.txt)...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [FEHLER] Beim Installieren der Requirements ist ein Fehler aufgetreten.
    echo Stelle sicher, dass du Internet hast.
    pause
    exit /b
)

:: ---------------------------------------------------
:: 4. PROGRAMM STARTEN
:: ---------------------------------------------------
:START_APP
echo.
echo [OK] Alles bereit! Starte GearCrate...
echo.
:: Ruft die start-browser.bat auf, da diese den korrekten Startbefehl enthält
call start-browser.bat

:: Falls start-browser.bat nicht existiert oder fehlschlägt, hier ein Fallback:
if %errorlevel% neq 0 (
    echo [!] start-browser.bat nicht gefunden oder fehlgeschlagen.
    echo Versuche direkten Start...
    python src/main.py
)

pause