import io
from models import Vocabulary


def export_to_anki(words: list[Vocabulary]) -> str:
    """Exportiert Vokabeln als Tab-separierte Textdatei für Anki-Import.

    Format: Russisch\tTransliteration\tDeutsch\tEnglisch\tWortart\tBeispiel_RU\tBeispiel_DE\tLevel\tTags
    """
    lines = []
    for word in words:
        fields = [
            word.russian.replace("\t", " "),
            word.transliteration.replace("\t", " "),
            word.german.replace("\t", " "),
            word.english.replace("\t", " "),
            word.word_type.replace("\t", " "),
            word.example_ru.replace("\t", " "),
            word.example_de.replace("\t", " "),
            word.level.replace("\t", " "),
            word.tags.replace("\t", " "),
        ]
        lines.append("\t".join(fields))

    return "\n".join(lines)
