@echo off
setlocal EnableDelayedExpansion
title GearCrate Setup

echo ====================================
echo   GearCrate - Installations-Setup
echo ====================================
echo.
echo Dieses Setup installiert automatisch:
echo - Python 3.12 (falls nicht vorhanden)
echo - Alle benoetigten Python-Pakete
echo - InvDetect Scanner-Komponenten
echo.
echo ====================================
echo.

:: ---------------------------------------------------
:: 1. PRÜFUNG: Ist Python installiert und aktuell genug?
:: ---------------------------------------------------
echo [1/3] Pruefe Python-Installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    goto :INSTALL_PYTHON
)

:: Prüfen ob Version >= 3.8 ist
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Deine Python-Version ist zu alt (mindestens 3.8 erforderlich).
    goto :INSTALL_PYTHON
)

:: Zeige installierte Python-Version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] !PYTHON_VERSION! gefunden.
echo.
goto :INSTALL_REQS

:: ---------------------------------------------------
:: 2. PYTHON INSTALLATION (falls nötig)
:: ---------------------------------------------------
:INSTALL_PYTHON
echo.
echo [!] Python wurde nicht gefunden oder ist veraltet.
echo [+] Lade Python 3.12.7 Installer herunter...
echo     (Dies kann einige Minuten dauern)
echo.

:: Temporären Ordner nutzen - AKTUALISIERTE VERSION
set "INSTALLER_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
set "INSTALLER_PATH=%TEMP%\python_installer.exe"

:: Download via PowerShell mit Fortschrittsanzeige
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%INSTALLER_PATH%'}"

if not exist "%INSTALLER_PATH%" (
    echo.
    echo [FEHLER] Download fehlgeschlagen!
    echo.
    echo Bitte installiere Python manuell:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Download abgeschlossen.
echo [+] Installiere Python 3.12.7...
echo     (Ein Installations-Fenster kann sich oeffnen)
echo.

:: Silent Install mit PATH Variable
start /wait "" "%INSTALLER_PATH%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo [OK] Python wurde installiert.
echo.
echo [WICHTIG] Das Setup-Skript wird jetzt neu gestartet,
echo           damit die PATH-Aenderungen wirksam werden.
echo.
del "%INSTALLER_PATH%"
pause

:: Startet das Skript neu
start "" "%~f0"
exit

:: ---------------------------------------------------
:: 3. REQUIREMENTS INSTALLIEREN
:: ---------------------------------------------------
:INSTALL_REQS
echo [2/3] Installiere Python-Pakete...
echo.
echo Dies kann einige Minuten dauern, besonders:
echo - EasyOCR (Deep Learning OCR)
echo - OpenCV (Computer Vision)
echo - PyTorch (wird von EasyOCR benoetigt)
echo.

:: Upgrade pip first
python -m pip install --upgrade pip --quiet

:: Install requirements
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo [FEHLER] Installation fehlgeschlagen!
    echo ====================================
    echo.
    echo Moegliche Ursachen:
    echo - Keine Internetverbindung
    echo - Firewall blockiert pip
    echo - Nicht genuegend Speicherplatz
    echo.
    echo Versuche es manuell mit:
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

:: ---------------------------------------------------
:: 4. SETUP ABGESCHLOSSEN
:: ---------------------------------------------------
:SETUP_COMPLETE
echo.
echo ====================================
echo   INSTALLATION ABGESCHLOSSEN!
echo ====================================
echo.
echo [3/3] Alle Komponenten wurden erfolgreich installiert.
echo.
echo ====================================
echo   NAECHSTE SCHRITTE
echo ====================================
echo.
echo Um GearCrate zu starten, fuehre bitte aus:
echo.
echo   ^>^> start-desktop-admin.bat
echo.
echo Diese Batch-Datei startet GearCrate mit
echo Administrator-Rechten (erforderlich fuer
echo den InvDetect Scanner).
echo.
echo ====================================
echo.
echo Druecke eine beliebige Taste zum Beenden...
pause >nul
