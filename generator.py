import json
import anthropic
from models import Vocabulary

SYSTEM_PROMPT = """Du bist ein Experte für Russisch als Fremdsprache. Du erstellst Vokabellisten für deutschsprachige Lernende.

Regeln:
- Verben immer als Aspektpaar angeben (imperfektiv / perfektiv), z.B. "читать / прочитать"
- Transliteration mit Betonungszeichen (é, á, ó, ú, ý), z.B. "chitát' / prochitát'"
- Bei Substantiven das grammatische Geschlecht angeben, z.B. "Substantiv (m.)" / "(f.)" / "(n.)"
- Englische Übersetzung im gleichen Stil wie die deutsche angeben (bei Verben beide Aspekte, z.B. "to read / to finish reading")
- Beispielsätze sollen dem angegebenen Level entsprechen (einfach für A1, komplexer für B2+)
- Sortierung nach Häufigkeit/Wichtigkeit (wichtigste zuerst)
- Keine Duplikate innerhalb der Liste

Antworte AUSSCHLIESSLICH mit einem JSON-Array. Kein anderer Text. Jedes Element hat diese Felder:
{
  "russian": "russisches Wort/Phrase",
  "transliteration": "Transliteration mit Betonung",
  "german": "deutsche Übersetzung",
  "english": "englische Übersetzung",
  "word_type": "Wortart (mit Geschlecht/Aspekt)",
  "example_ru": "Beispielsatz auf Russisch",
  "example_de": "Beispielsatz auf Deutsch",
  "level": "A1/A2/B1/B2/C1/C2",
  "tags": "Thema/Kategorie"
}"""

MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 25  # Sichere Anzahl pro API-Aufruf


def parse_response(text: str) -> list[Vocabulary]:
    """Parst die Claude-Antwort als JSON-Array von Vokabeln."""
    text = text.strip()
    # Falls Claude den JSON in Markdown-Codeblock einpackt
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    data = json.loads(text)
    return [Vocabulary(**item) for item in data]


async def generate_vocabulary(
    api_key: str,
    prompt: str,
    count: int = 30,
) -> list[Vocabulary]:
    """Generiert Vokabeln basierend auf einer freien Anfrage."""
    client = anthropic.AsyncAnthropic(api_key=api_key)
    all_words: list[Vocabulary] = []
    remaining = count

    batch_num = 0
    while remaining > 0:
        batch_size = min(remaining, BATCH_SIZE)
        batch_num += 1

        if batch_num == 1:
            user_prompt = f"""Erstelle genau {batch_size} russische Vokabeln basierend auf dieser Anfrage:

{prompt}

Gib genau {batch_size} Einträge zurück als JSON-Array."""
        else:
            # Bei Folge-Batches: bereits generierte Wörter ausschließen
            existing = [w.russian for w in all_words]
            user_prompt = f"""Erstelle genau {batch_size} WEITERE russische Vokabeln basierend auf dieser Anfrage:

{prompt}

Diese Wörter hast du bereits generiert (NICHT wiederholen):
{", ".join(existing)}

Gib genau {batch_size} neue Einträge zurück als JSON-Array."""

        response = await client.messages.create(
            model=MODEL,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        words = parse_response(response.content[0].text)
        all_words.extend(words)
        remaining -= len(words)

    return all_words[:count]
