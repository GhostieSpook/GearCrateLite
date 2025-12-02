@echo off
:: ====================================
:: AUTO-ADMIN CHECK
:: ====================================
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if %errorlevel% neq 0 (
    echo Fordere Administrator-Rechte an...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ====================================
:: AB HIER LAUFT ES ALS ADMIN
:: ====================================

setlocal EnableDelayedExpansion
title GearCrate Setup - 2025 Edition

:: LOG-DATEI INITIALISIEREN
set "LOGFILE=%~dp0setup-log.txt"
echo ========================================= > "%LOGFILE%"
echo GearCrate Setup Log >> "%LOGFILE%"
echo Started: %date% %time% >> "%LOGFILE%"
echo ========================================= >> "%LOGFILE%"
echo. >> "%LOGFILE%"

echo =========================================
echo       GearCrate - Installation Setup
echo =========================================
echo.
echo Works with Python 3.8 to 3.13
echo Your existing Python will be kept if greater than or equal to 3.8
echo.
echo =========================================
echo.
echo Writing log to: setup-log.txt
echo.

echo [LOG] Setup started as Administrator >> "%LOGFILE%"

:: ---------------------------------------------------
:: 1. Check Python (greater than or equal to 3.8)
:: ---------------------------------------------------
echo [1/3] Checking Python installation...
echo [1/3] Checking Python installation... >> "%LOGFILE%"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found.
    echo [ERROR] Python not found >> "%LOGFILE%"
    goto :ASK_INSTALL_PYTHON
)

echo [LOG] Python found, checking version... >> "%LOGFILE%"

python -c "import sys; v = sys.version_info; exit^(0 if ^(v.major > 3 or ^(v.major == 3 and v.minor >= 8^)^) else 1^)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python version too old (3.8 or newer required).
    echo [ERROR] Python version too old >> "%LOGFILE%"
    goto :ASK_INSTALL_PYTHON
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
echo [OK] Python !PYTHON_VERSION! detected - excellent, continuing!
echo [OK] Python !PYTHON_VERSION! detected >> "%LOGFILE%"
echo.
goto :INSTALL_REQS

:: ---------------------------------------------------
:: Ask if user wants auto-install (now 3.11.9)
:: ---------------------------------------------------
:ASK_INSTALL_PYTHON
echo. >> "%LOGFILE%"
echo [LOG] Asking user to install Python... >> "%LOGFILE%"
echo.
echo No compatible Python found.
echo Do you want to download and install Python 3.11.9 automatically?
echo (Recommended - very stable and widely compatible)
echo.
choice /c YN /n /m " [Y] Yes, install Python 3.11.9    [N] No, I'll install it myself "
if %errorlevel%==1 (
    echo [LOG] User chose to install Python >> "%LOGFILE%"
    goto :INSTALL_PYTHON
)
if %errorlevel%==2 (
    echo [LOG] User chose manual installation >> "%LOGFILE%"
    goto :MANUAL_PYTHON
)

:: ---------------------------------------------------
:: 2 Download + install Python 3.11.9
:: ---------------------------------------------------
:INSTALL_PYTHON
echo. >> "%LOGFILE%"
echo [LOG] Starting Python download... >> "%LOGFILE%"
echo.
echo [+] Downloading Python 3.11.9 (64-bit) ...
set "INSTALLER_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "INSTALLER_PATH=%TEMP%\python-3.11.9-installer.exe"

echo [LOG] Download URL: %INSTALLER_URL% >> "%LOGFILE%"
echo [LOG] Target path: %INSTALLER_PATH% >> "%LOGFILE%"

powershell -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%INSTALLER_URL%' -OutFile '%INSTALLER_PATH%' -UseBasicParsing"

if not exist "%INSTALLER_PATH%" (
    echo.
    echo [ERROR] Download failed!
    echo [ERROR] Python download failed >> "%LOGFILE%"
    echo Please install Python manually: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Download finished.
echo [LOG] Download completed successfully >> "%LOGFILE%"
echo [+] Installing Python 3.11.9 silently...
echo [LOG] Starting Python installation... >> "%LOGFILE%"
start /wait "" "%INSTALLER_PATH%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1

del "%INSTALLER_PATH%" 2>nul
echo [LOG] Installation completed, installer deleted >> "%LOGFILE%"

echo.
echo [OK] Python 3.11.9 installed successfully.
echo      Restarting setup so the new PATH is active...
echo.
echo [LOG] Python installed, restarting setup... >> "%LOGFILE%"
pause
start "" "%~f0"
exit

:: ---------------------------------------------------
:: User prefers manual installation
:: ---------------------------------------------------
:MANUAL_PYTHON
echo.
echo Okay - just install Python 3.11 or 3.12 from
echo https://www.python.org/downloads/
echo and make sure "Add Python to PATH" is checked.
echo.
echo Then simply run this setup.bat again.
echo.
echo [LOG] User will install Python manually >> "%LOGFILE%"
pause
exit /b 0

:: ---------------------------------------------------
:: 3 Install packages
:: ---------------------------------------------------
:INSTALL_REQS
echo [2/3] Installing required Python packages (3-10 minutes)...
echo [2/3] Installing Python packages... >> "%LOGFILE%"
echo.

echo [LOG] Upgrading pip... >> "%LOGFILE%"
python -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip >> "%LOGFILE%"
)

echo [LOG] Installing requirements.txt... >> "%LOGFILE%"
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo.
    echo =========================================
    echo [ERROR] Failed to install packages!
    echo =========================================
    echo [ERROR] Package installation failed >> "%LOGFILE%"
    echo Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [LOG] All packages installed successfully >> "%LOGFILE%"

:: ---------------------------------------------------
:: 4 Finished
:: ---------------------------------------------------
echo.
echo =========================================
echo        INSTALLATION COMPLETED!
echo =========================================
echo.
echo Start GearCrate with administrator rights:
echo.
echo       start-desktop-admin.bat
echo.
echo.
echo Happy hunting in Star Citizen!
echo.
echo [LOG] Setup completed successfully >> "%LOGFILE%"
echo [LOG] Finished: %date% %time% >> "%LOGFILE%"
pause
