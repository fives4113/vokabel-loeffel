from pydantic import BaseModel
from enum import Enum


class WordType(str, Enum):
    NOUN = "Substantiv"
    VERB = "Verb"
    ADJECTIVE = "Adjektiv"
    ADVERB = "Adverb"
    PRONOUN = "Pronomen"
    PREPOSITION = "Präposition"
    CONJUNCTION = "Konjunktion"
    NUMERAL = "Zahlwort"
    PARTICLE = "Partikel"
    INTERJECTION = "Interjektion"
    PHRASE = "Redewendung"


class Vocabulary(BaseModel):
    russian: str  # z.B. "говорить / сказать"
    transliteration: str  # z.B. "govorít' / skazát'"
    german: str  # z.B. "sprechen / sagen"
    english: str = ""  # z.B. "to speak / to say"
    word_type: str  # z.B. "Verb (impf./pf.)"
    example_ru: str  # z.B. "Она говорит по-русски."
    example_de: str  # z.B. "Sie spricht Russisch."
    level: str  # z.B. "A1"
    tags: str  # z.B. "Kommunikation"


class GenerateRequest(BaseModel):
    prompt: str  # z.B. "100 wichtigste Vokabeln A1"
    count: int = 30  # Anzahl pro Batch


class ExtractRequest(BaseModel):
    filename: str  # Name der hochgeladenen Datei


class VocabularyResponse(BaseModel):
    words: list[Vocabulary]
    duplicates_removed: int = 0
    total_generated: int = 0
