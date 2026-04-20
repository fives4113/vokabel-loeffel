import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse, Response
from pydantic import BaseModel
from models import GenerateRequest, VocabularyResponse, Vocabulary
from generator import generate_vocabulary
from extractor import extract_from_document
from database import (
    filter_duplicates,
    mark_exported,
    get_exported_count,
    clear_exported,
    get_all_exported,
)
from exporter import export_to_anki
from apkg_exporter import export_to_apkg
from config import load_api_key


class ApkgExportRequest(BaseModel):
    words: list[Vocabulary]
    deck_name: str = "Russisch Vokabeln"

app = FastAPI(title="Vokabel Löffel — Russisch-Vokabelgenerator")

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def get_api_key() -> str:
    key = load_api_key()
    if not key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY ist nicht konfiguriert. Bitte Server über start.sh/start.bat neu starten und Key eingeben.",
        )
    return key


@app.post("/api/generate", response_model=VocabularyResponse)
async def api_generate(request: GenerateRequest):
    """Modus 1: Vokabeln aus freier Anfrage generieren."""
    api_key = get_api_key()
    words = await generate_vocabulary(api_key, request.prompt, request.count)
    total = len(words)
    words, dupes = filter_duplicates(words)
    return VocabularyResponse(
        words=words,
        duplicates_removed=dupes,
        total_generated=total,
    )


@app.post("/api/extract", response_model=VocabularyResponse)
async def api_extract(file: UploadFile = File(...)):
    """Modus 2: Vokabeln aus hochgeladenem Dokument extrahieren."""
    api_key = get_api_key()

    # Datei speichern
    filepath = UPLOAD_DIR / file.filename
    content = await file.read()
    filepath.write_bytes(content)

    try:
        words = await extract_from_document(api_key, file.filename)
        total = len(words)
        words, dupes = filter_duplicates(words)
        return VocabularyResponse(
            words=words,
            duplicates_removed=dupes,
            total_generated=total,
        )
    finally:
        # Upload aufräumen
        filepath.unlink(missing_ok=True)


@app.post("/api/export")
async def api_export(words: list[Vocabulary]):
    """Exportiert Vokabeln als Anki-kompatible TSV-Datei."""
    tsv_content = export_to_anki(words)
    mark_exported(words)
    return PlainTextResponse(
        content=tsv_content,
        media_type="text/tab-separated-values",
        headers={"Content-Disposition": "attachment; filename=russisch_vokabeln.txt"},
    )


@app.post("/api/export-apkg")
async def api_export_apkg(request: ApkgExportRequest):
    """Exportiert Vokabeln als Anki-Paket (.apkg) inkl. Notiztyp und Styling."""
    apkg_bytes = export_to_apkg(request.words, request.deck_name)
    mark_exported(request.words)
    return Response(
        content=apkg_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=russisch_vokabeln.apkg"},
    )


@app.get("/api/history")
async def api_history():
    """Liefert alle bereits gespeicherten Vokabeln."""
    words = get_all_exported()
    return {"words": words, "count": len(words)}


@app.post("/api/reset")
async def api_reset():
    """Leert die Vokabel-Bibliothek."""
    clear_exported()
    return {"message": "Bibliothek geleert."}


@app.get("/api/stats")
async def api_stats():
    return {"exported_count": get_exported_count()}


# Statische Dateien (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
