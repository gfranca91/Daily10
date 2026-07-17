import unicodedata
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.85


def _normalize(text: str) -> str:
    text = text.strip().lower()
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def check_translation_answer(
    correct_translation: str,
    user_answer: str,
    threshold: float = SIMILARITY_THRESHOLD,
) -> dict:
    """Compara a tradução correta com a resposta do usuário e decide se acertou.

    Usa SequenceMatcher para tolerar pequenos erros de digitação (ex: "gato" vs "gto").
    Ignora acentos (ex: "ola" conta como "olá") — comum ao digitar rápido no celular.
    """
    normalized_correct = _normalize(correct_translation)
    normalized_answer = _normalize(user_answer)

    similarity = SequenceMatcher(None, normalized_correct, normalized_answer).ratio()

    return {
        "correct": similarity >= threshold,
        "similarity": round(similarity, 4),
    }
