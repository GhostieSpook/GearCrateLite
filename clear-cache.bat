@echo off
echo ======================================
echo Python Cache Cleaner
echo ======================================
echo.
echo Loesche Python Cache Dateien...
echo.

cd /d "%~dp0"

:: Delete .pyc files
for /r "src" %%f in (*.pyc) do (
    echo Deleting: %%f
    del /f /q "%%f" 2>nul
)

:: Delete __pycache__ directories
for /d /r "src" %%d in (__pycache__) do (
    echo Deleting directory: %%d
    rd /s /q "%%d" 2>nul
)

echo.
echo Fertig!
echo.
pause
