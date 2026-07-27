from sqlalchemy import text

from app.db import SessionLocal
from app.services.cefr import LEVEL_ORDER

_SELECT_FIELDS = "id, language_code, term, translation_pt, example_sentence, frequency_rank"

# Mapeia cefr_level pra um número (A1=1 ... C2=6) pra poder comparar/ordenar níveis em SQL.
_LEVEL_RANK_CASE = "CASE cefr_level " + " ".join(f"WHEN '{lvl}' THEN {i + 1}" for i, lvl in enumerate(LEVEL_ORDER)) + " END"


def get_word_by_id(word_id: int) -> dict | None:
    with SessionLocal() as db:
        row = db.execute(
            text(f"SELECT {_SELECT_FIELDS} FROM words WHERE id = :id"),
            {"id": word_id},
        ).mappings().first()
        return dict(row) if row else None


def get_unseen_words(user_id: int, limit: int, min_level: str) -> list[dict]:
    """Palavras do nível atual do usuário em diante (cascata: se o nível atual esgotar,
    passa pro próximo), ainda não vistas (sem linha em user_word_progress), ordenadas por
    nível e depois por frequency_rank."""
    min_level_rank = LEVEL_ORDER.index(min_level) + 1
    with SessionLocal() as db:
        rows = db.execute(
            text(
                f"""
                SELECT {_SELECT_FIELDS} FROM words w
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_word_progress p
                    WHERE p.word_id = w.id AND p.user_id = :user_id
                )
                AND {_LEVEL_RANK_CASE.replace("cefr_level", "w.cefr_level")} >= :min_level_rank
                ORDER BY {_LEVEL_RANK_CASE.replace("cefr_level", "w.cefr_level")}, w.frequency_rank
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit, "min_level_rank": min_level_rank},
        ).mappings().all()
        return [dict(row) for row in rows]


def get_next_word_at_level(level: str, exclude_ids: list[int]) -> dict | None:
    """Próxima palavra (menor frequency_rank) de um nível CEFR específico, usada no teste
    de nivelamento adaptativo por nível. Não olha progresso — o teste roda uma vez, antes
    de qualquer lição."""
    with SessionLocal() as db:
        row = db.execute(
            text(
                f"""
                SELECT {_SELECT_FIELDS} FROM words w
                WHERE w.cefr_level = :level
                AND w.id != ALL(:exclude_ids)
                ORDER BY w.frequency_rank
                LIMIT 1
                """
            ),
            {"level": level, "exclude_ids": exclude_ids or [0]},
        ).mappings().first()
        return dict(row) if row else None


def get_words_by_ids(word_ids: list[int]) -> list[dict]:
    if not word_ids:
        return []
    with SessionLocal() as db:
        rows = db.execute(
            text(f"SELECT {_SELECT_FIELDS} FROM words WHERE id = ANY(:ids) ORDER BY frequency_rank"),
            {"ids": word_ids},
        ).mappings().all()
        return [dict(row) for row in rows]


