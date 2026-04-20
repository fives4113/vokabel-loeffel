import json
import os
from pathlib import Path


def config_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "VokabelLoeffel"
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "vokabel-loeffel"


def config_file() -> Path:
    return config_dir() / "config.json"


def load_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    path = config_file()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return (data.get("anthropic_api_key") or "").strip()
        except (OSError, json.JSONDecodeError):
            return ""
    return ""


def save_api_key(key: str) -> Path:
    path = config_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"anthropic_api_key": key.strip()}),
        encoding="utf-8",
    )
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path
