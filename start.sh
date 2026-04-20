#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

PY=".venv/bin/python"

ask() {
    local ans
    read -r -p "$1 [j/n] " ans
    case "$ans" in
        j|J|y|Y|ja|Ja|yes|Yes) return 0 ;;
        *) return 1 ;;
    esac
}

install_deps() {
    "$PY" -m ensurepip --upgrade >/dev/null 2>&1 || true
    "$PY" -m pip install --upgrade pip
    "$PY" -m pip install -r requirements.txt
}

if [ ! -d .venv ]; then
    echo "Keine virtuelle Umgebung gefunden (.venv fehlt)."
    echo "Benötigt: Pakete aus requirements.txt."
    if ask "Jetzt .venv anlegen und Abhängigkeiten installieren?"; then
        python3 -m venv .venv
        install_deps
    else
        echo "Abbruch."
        exit 1
    fi
else
    if ! "$PY" check_deps.py; then
        if ask "Fehlende/veraltete Pakete jetzt installieren?"; then
            install_deps
        else
            echo "Abbruch."
            exit 1
        fi
    fi
fi

if ! "$PY" -c "import sys; from config import load_api_key; sys.exit(0 if load_api_key() else 1)"; then
    echo "Kein ANTHROPIC_API_KEY gefunden."
    read -r -p "Bitte API-Key eingeben (sk-ant-...): " VL_KEY
    if [ -z "$VL_KEY" ]; then
        echo "Kein Key eingegeben. Abbruch."
        exit 1
    fi
    VL_KEY="$VL_KEY" "$PY" -c "import os; from config import save_api_key; print('Gespeichert in:', save_api_key(os.environ['VL_KEY']))"
    unset VL_KEY
fi

echo "Vokabel Löffel läuft auf http://127.0.0.1:8000  (Strg+C zum Beenden)"
exec .venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --reload
