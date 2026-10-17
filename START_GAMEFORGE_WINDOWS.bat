@echo off
chcp 65001 >nul
cd /d "%~dp0"
title GAMEFORGE 2.0
set "PYEXE="

rem 1) Python-Launcher (offizielle Python-Installation)
py -3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 (
    py -3 app.py %*
    goto :ende
)

rem 2) python im PATH (der Microsoft-Store-Platzhalter wird hier sicher erkannt und uebersprungen)
python -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 (
    python app.py %*
    goto :ende
)

rem 3) Das mit Blender mitgelieferte Python verwenden (neueste Blender-Version)
for /d %%D in ("%ProgramFiles%\Blender Foundation\Blender*") do (
    for /d %%V in ("%%D\*") do (
        if exist "%%V\python\bin\python.exe" set "PYEXE=%%V\python\bin\python.exe"
    )
)
if defined PYEXE (
    echo Kein eigenes Python gefunden. GAMEFORGE nutzt das in Blender enthaltene Python:
    echo   %PYEXE%
    echo.
    "%PYEXE%" app.py %*
    goto :ende
)

echo Python 3.11 oder neuer wird benoetigt.
echo Python installieren: https://www.python.org/downloads/windows/
echo Bei der Installation "Add python.exe to PATH" aktivieren.
pause
exit /b 1

:ende
if errorlevel 1 (
    echo.
    echo GAMEFORGE wurde mit einem Fehler beendet. Die Meldung steht oben.
    pause
)
