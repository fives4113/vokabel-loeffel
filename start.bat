@echo off
setlocal
cd /d "%~dp0"

set PY=.venv\Scripts\python.exe

if not exist .venv goto NO_VENV
"%PY%" check_deps.py
if errorlevel 1 goto ASK_INSTALL_DEPS
goto CHECK_KEY

:NO_VENV
echo Keine virtuelle Umgebung gefunden (.venv fehlt).
echo Benoetigt: Pakete aus requirements.txt.
set /p ANS=Jetzt .venv anlegen und Abhaengigkeiten installieren? [j/n]:
if /i "%ANS%"=="j" goto DO_CREATE
if /i "%ANS%"=="y" goto DO_CREATE
echo Abbruch.
pause
exit /b 1

:DO_CREATE
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Python wurde nicht gefunden. Installiere Python 3.10+ von python.org.
    pause
    exit /b 1
)
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
goto CHECK_KEY

:ASK_INSTALL_DEPS
set /p ANS=Fehlende/veraltete Pakete jetzt installieren? [j/n]:
if /i "%ANS%"=="j" goto DO_INSTALL
if /i "%ANS%"=="y" goto DO_INSTALL
echo Abbruch.
pause
exit /b 1

:DO_INSTALL
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
goto CHECK_KEY

:CHECK_KEY
"%PY%" -c "import sys; from config import load_api_key; sys.exit(0 if load_api_key() else 1)"
if errorlevel 1 goto ASK_KEY
goto RUN

:ASK_KEY
echo Kein ANTHROPIC_API_KEY gefunden.
set /p VL_KEY=Bitte API-Key eingeben (sk-ant-...):
if "%VL_KEY%"=="" (
    echo Kein Key eingegeben. Abbruch.
    pause
    exit /b 1
)
"%PY%" -c "import os; from config import save_api_key; print('Gespeichert in:', save_api_key(os.environ['VL_KEY']))"
set VL_KEY=

:RUN
echo Vokabel Loeffel laeuft auf http://127.0.0.1:8000  (Strg+C zum Beenden)
.venv\Scripts\uvicorn app:app --host 127.0.0.1 --port 8000 --reload
