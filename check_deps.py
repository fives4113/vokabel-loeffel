"""Prüft, ob alle Einträge aus requirements.txt installiert sind.

Exitcode 0 = alles ok, 1 = fehlend/zu alt. Gibt Probleme auf stderr aus.
"""
import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

try:
    from packaging.requirements import Requirement
    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False


def parse_name(line: str) -> str:
    for sep in (">=", "==", "~=", ">", "<=", "<"):
        if sep in line:
            return line.split(sep, 1)[0].strip()
    return line.strip()


def main() -> int:
    req_file = Path(__file__).parent / "requirements.txt"
    issues: list[str] = []

    for raw in req_file.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        if HAS_PACKAGING:
            req = Requirement(line)
            name = req.name
            try:
                installed = version(name)
            except PackageNotFoundError:
                issues.append(f"{name} fehlt")
                continue
            if req.specifier and not req.specifier.contains(installed, prereleases=True):
                issues.append(f"{name} {installed} erfüllt nicht {req.specifier}")
        else:
            name = parse_name(line)
            try:
                version(name)
            except PackageNotFoundError:
                issues.append(f"{name} fehlt")

    if issues:
        print("Fehlende oder veraltete Abhängigkeiten:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
