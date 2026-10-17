@echo off
rem GAMEFORGE-Werkzeug: sucht ein passendes Python (3.11+) und startet gf.py.
setlocal
set "GF=%~dp0gf.py"
set "PYEXE="
py -3 -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto :mitpy
python -c "import sys;raise SystemExit(0 if sys.version_info>=(3,11) else 1)" >nul 2>nul
if not errorlevel 1 goto :mitpython
for /d %%D in ("%ProgramFiles%\Blender Foundation\Blender*") do for /d %%V in ("%%D\*") do if exist "%%V\python\bin\python.exe" set "PYEXE=%%V\python\bin\python.exe"
if defined PYEXE goto :mitblender
echo Kein Python 3.11+ gefunden (weder installiert noch in Blender).
exit /b 1
:mitpy
py -3 "%GF%" %*
exit /b %errorlevel%
:mitpython
python "%GF%" %*
exit /b %errorlevel%
:mitblender
"%PYEXE%" "%GF%" %*
exit /b %errorlevel%
