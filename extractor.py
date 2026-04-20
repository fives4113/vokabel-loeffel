import json
import base64
from pathlib import Path
import anthropic
import fitz  # pymupdf
from models import Vocabulary
from generator import SYSTEM_PROMPT, MODEL, parse_response

UPLOAD_DIR = Path(__file__).parent / "uploads"

EXTRACT_PROMPT = """Analysiere den folgenden Text aus einem Russisch-Lehrbuch oder Arbeitsheft.
Extrahiere die wichtigsten Vokabeln daraus und erstelle eine Vokabelliste.

Konzentriere dich auf:
- Neue Vokabeln die im Text eingeführt oder verwendet werden
- Schlüsselwörter die für das Thema relevant sind
- Ignoriere Aufgabenstellungen, Grammatik-Erklärungen und Meta-Text

Gib die Vokabeln als JSON-Array zurück (gleiches Format wie im System-Prompt)."""


def extract_text_from_pdf(filepath: Path) -> str:
    """Extrahiert Text aus einer PDF-Datei."""
    doc = fitz.open(str(filepath))
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n\n".join(text_parts)


def encode_image(filepath: Path) -> tuple[str, str]:
    """Liest ein Bild und gibt (base64_data, media_type) zurück."""
    suffix = filepath.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_types.get(suffix, "image/jpeg")
    data = base64.standard_b64encode(filepath.read_bytes()).decode()
    return data, media_type


async def extract_from_document(
    api_key: str,
    filename: str,
) -> list[Vocabulary]:
    """Extrahiert Vokabeln aus einem hochgeladenen Dokument."""
    filepath = UPLOAD_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {filename}")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        text = extract_text_from_pdf(filepath)
        messages = [
            {
                "role": "user",
                "content": f"{EXTRACT_PROMPT}\n\n---\n\nTEXT AUS DEM DOKUMENT:\n\n{text}",
            }
        ]
    elif suffix in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
        image_data, media_type = encode_image(filepath)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACT_PROMPT,
                    },
                ],
            }
        ]
    else:
        # Textdatei direkt lesen
        text = filepath.read_text(encoding="utf-8")
        messages = [
            {
                "role": "user",
                "content": f"{EXTRACT_PROMPT}\n\n---\n\nTEXT AUS DEM DOKUMENT:\n\n{text}",
            }
        ]

    response = await client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return parse_response(response.content[0].text)
