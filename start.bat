@echo off
setlocal
cd /d "%~dp0"

set PY=.venv\Scripts\python.exe

if not exist .venv goto NO_VENV
"%PY%" check_deps.py
if errorlevel 1 goto ASK_INSTALL_DEPS
goto CHECK_KEY

:NO_VENV
echo.
echo Keine virtuelle Umgebung gefunden ^(.venv fehlt^).
echo Benoetigt: Pakete aus requirements.txt.
echo.
choice /c jn /n /m "Jetzt .venv anlegen und Abhaengigkeiten installieren? [j/n] "
if errorlevel 2 goto ABORT
python -m venv .venv
if errorlevel 1 (
    echo.
    echo ERROR: Python wurde nicht gefunden. Installiere Python 3.10+ von python.org.
    pause
    exit /b 1
)
call :INSTALL_DEPS
if errorlevel 1 goto FAIL
goto CHECK_KEY

:ASK_INSTALL_DEPS
echo.
choice /c jn /n /m "Fehlende/veraltete Pakete jetzt installieren? [j/n] "
if errorlevel 2 goto ABORT
call :INSTALL_DEPS
if errorlevel 1 goto FAIL
goto CHECK_KEY

:INSTALL_DEPS
"%PY%" -m ensurepip --upgrade >nul 2>&1
"%PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo ERROR: pip konnte nicht geladen werden. Stelle sicher, dass Python vollstaendig
    echo installiert ist ^(Haken bei "pip" im python.org-Installer^).
    exit /b 1
)
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
exit /b 0

:CHECK_KEY
"%PY%" -c "import sys; from config import load_api_key; sys.exit(0 if load_api_key() else 1)"
if errorlevel 1 goto ASK_KEY
goto RUN

:ASK_KEY
echo.
echo Kein ANTHROPIC_API_KEY gefunden.
set /p "VL_KEY=Bitte API-Key eingeben (sk-ant-...): "
if "%VL_KEY%"=="" goto KEY_ABORT
"%PY%" -c "import os; from config import save_api_key; print('Gespeichert in:', save_api_key(os.environ['VL_KEY']))"
if errorlevel 1 (
    set VL_KEY=
    echo Speichern fehlgeschlagen.
    pause
    exit /b 1
)
set VL_KEY=
goto RUN

:KEY_ABORT
echo Kein Key eingegeben. Abbruch.
pause
exit /b 1

:ABORT
echo Abbruch.
pause
exit /b 1

:FAIL
echo.
echo Installation fehlgeschlagen. Siehe Fehlermeldungen oben.
pause
exit /b 1

:RUN
echo.
echo Vokabel Loeffel laeuft auf http://127.0.0.1:8000  ^(Strg+C zum Beenden^)
echo.
.venv\Scripts\uvicorn app:app --host 127.0.0.1 --port 8000 --reload
if errorlevel 1 pause
