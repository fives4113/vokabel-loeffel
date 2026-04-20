import io
import genanki
from models import Vocabulary

MODEL_ID = 1733501234590
DECK_ID_BASE = 1733501234568

FRONT_RU_DE = """\
<div class="russian">{{Russisch}}</div>
<div class="translit">{{Transliteration}}</div>
<div class="type">{{Wortart}}</div>
"""

BACK_RU_DE = """\
{{FrontSide}}
<hr id="answer">
<div class="german">{{Deutsch}}</div>
{{#Englisch}}<div class="english">{{Englisch}}</div>{{/Englisch}}
<div class="example">
  <div class="example-ru">{{BeispielRU}}</div>
  <div class="example-de">{{BeispielDE}}</div>
</div>
<div class="level">{{Level}}</div>
"""

FRONT_DE_RU = """\
<div class="german">{{Deutsch}}</div>
{{#Englisch}}<div class="english">{{Englisch}}</div>{{/Englisch}}
<div class="type">{{Wortart}}</div>
"""

BACK_DE_RU = """\
{{FrontSide}}
<hr id="answer">
<div class="russian">{{Russisch}}</div>
<div class="translit">{{Transliteration}}</div>
<div class="example">
  <div class="example-ru">{{BeispielRU}}</div>
  <div class="example-de">{{BeispielDE}}</div>
</div>
<div class="level">{{Level}}</div>
"""

CSS = """\
.card {
    font-family: 'Segoe UI', Arial, sans-serif;
    text-align: center;
    padding: 2em;
    background: #fafafa;
    color: #222;
}
.russian { font-size: 2em; color: #1a237e; margin-bottom: 0.2em; }
.translit { font-size: 1.1em; color: #666; font-style: italic; }
.german { font-size: 1.8em; color: #2e7d32; margin: 0.5em 0 0.1em; }
.english { font-size: 1.15em; color: #8a5a00; font-style: italic; margin: 0 0 0.4em; }
.type { font-size: 0.9em; color: #777; margin-top: 0.5em; }
.example { margin-top: 1em; padding: 1em; background: #f0f0f0; border-radius: 8px; text-align: left; }
.example-ru { font-size: 1.1em; margin-bottom: 0.3em; }
.example-de { color: #555; font-style: italic; }
.level { margin-top: 1em; font-size: 0.8em; color: #888; }

.nightMode.card, .night_mode .card { background: #1e1e1e; color: #eee; }
.nightMode .russian, .night_mode .russian { color: #8ab4f8; }
.nightMode .translit, .night_mode .translit { color: #bbb; }
.nightMode .german, .night_mode .german { color: #81c995; }
.nightMode .english, .night_mode .english { color: #f9ab00; }
.nightMode .type, .night_mode .type { color: #aaa; }
.nightMode .example, .night_mode .example { background: #2a2a2a; }
.nightMode .example-de, .night_mode .example-de { color: #ccc; }
.nightMode .level, .night_mode .level { color: #999; }
"""

MODEL = genanki.Model(
    MODEL_ID,
    "Russisch Vokabel",
    fields=[
        {"name": "Russisch"},
        {"name": "Transliteration"},
        {"name": "Deutsch"},
        {"name": "Englisch"},
        {"name": "Wortart"},
        {"name": "BeispielRU"},
        {"name": "BeispielDE"},
        {"name": "Level"},
        {"name": "Tags"},
    ],
    templates=[
        {"name": "Russisch → Deutsch", "qfmt": FRONT_RU_DE, "afmt": BACK_RU_DE},
        {"name": "Deutsch → Russisch", "qfmt": FRONT_DE_RU, "afmt": BACK_DE_RU},
    ],
    css=CSS,
)


def sanitize_tag(tag: str) -> str:
    """Anki-Tags dürfen keine Whitespaces enthalten."""
    return "_".join(tag.split())


def export_to_apkg(words: list[Vocabulary], deck_name: str) -> bytes:
    """Erstellt ein Anki-Paket (.apkg) inkl. Notiztyp, Kartenvorlagen und Styling."""
    deck = genanki.Deck(DECK_ID_BASE, deck_name)
    for word in words:
        tags = [sanitize_tag(t) for t in word.tags.split(",") if t.strip()]
        note = genanki.Note(
            model=MODEL,
            fields=[
                word.russian,
                word.transliteration,
                word.german,
                word.english,
                word.word_type,
                word.example_ru,
                word.example_de,
                word.level,
                word.tags,
            ],
            tags=tags,
        )
        deck.add_note(note)

    buf = io.BytesIO()
    genanki.Package(deck).write_to_file(buf)
    return buf.getvalue()
