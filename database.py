import sqlite3
from pathlib import Path
from models import Vocabulary

DB_PATH = Path(__file__).parent / "data" / "vocabulary.db"

COLUMNS = [
    ("russian", "TEXT NOT NULL"),
    ("transliteration", "TEXT DEFAULT ''"),
    ("german", "TEXT NOT NULL"),
    ("english", "TEXT DEFAULT ''"),
    ("word_type", "TEXT DEFAULT ''"),
    ("example_ru", "TEXT DEFAULT ''"),
    ("example_de", "TEXT DEFAULT ''"),
    ("level", "TEXT DEFAULT ''"),
    ("tags", "TEXT DEFAULT ''"),
]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS exported_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            russian TEXT NOT NULL,
            german TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(russian, german)
        )
    """)
    existing = {row[1] for row in conn.execute("PRAGMA table_info(exported_words)").fetchall()}
    for name, definition in COLUMNS:
        if name not in existing:
            conn.execute(f"ALTER TABLE exported_words ADD COLUMN {name} {definition}")
    conn.commit()
    return conn


def filter_duplicates(words: list[Vocabulary]) -> tuple[list[Vocabulary], int]:
    """Filtert bereits exportierte Vokabeln raus. Gibt (neue_wörter, anzahl_duplikate) zurück."""
    conn = get_connection()
    cursor = conn.cursor()

    new_words = []
    duplicate_count = 0

    for word in words:
        cursor.execute(
            "SELECT 1 FROM exported_words WHERE russian = ?",
            (word.russian,),
        )
        if cursor.fetchone() is None:
            new_words.append(word)
        else:
            duplicate_count += 1

    conn.close()
    return new_words, duplicate_count


def mark_exported(words: list[Vocabulary]) -> None:
    """Speichert exportierte Vokabeln (alle Felder) in der Datenbank."""
    conn = get_connection()
    for word in words:
        conn.execute(
            """
            INSERT INTO exported_words
                (russian, transliteration, german, english, word_type, example_ru, example_de, level, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(russian, german) DO UPDATE SET
                transliteration = excluded.transliteration,
                english = excluded.english,
                word_type = excluded.word_type,
                example_ru = excluded.example_ru,
                example_de = excluded.example_de,
                level = excluded.level,
                tags = excluded.tags
            """,
            (
                word.russian,
                word.transliteration,
                word.german,
                word.english,
                word.word_type,
                word.example_ru,
                word.example_de,
                word.level,
                word.tags,
            ),
        )
    conn.commit()
    conn.close()


def get_exported_count() -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM exported_words")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_all_exported() -> list[Vocabulary]:
    """Liefert alle gespeicherten Vokabeln, neueste zuerst."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT russian, transliteration, german, english, word_type,
               example_ru, example_de, level, tags
        FROM exported_words
        ORDER BY created_at DESC, id DESC
        """
    ).fetchall()
    conn.close()
    return [Vocabulary(**dict(row)) for row in rows]


def clear_exported() -> None:
    """Löscht alle exportierten Vokabeln."""
    conn = get_connection()
    conn.execute("DELETE FROM exported_words")
    conn.commit()
    conn.close()
