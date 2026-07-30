import unicodedata
from difflib import SequenceMatcher

COGNATE_THRESHOLD = 0.90


def _normalize(text: str) -> str:
    text = text.strip().lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def is_cognate(term: str, translation_pt: str) -> bool:
    """Palavra em espanhol muito parecida com a tradução em português (>=90% de
    similaridade, ignorando acentos) — não agrega valor pedagógico nos exercícios,
    já que o usuário praticamente já sabe a palavra."""
    first_translation = translation_pt.split("/")[0].strip()
    ratio = SequenceMatcher(None, _normalize(term), _normalize(first_translation)).ratio()
    return ratio >= COGNATE_THRESHOLD
