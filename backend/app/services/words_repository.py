from sqlalchemy import text

from app.db import SessionLocal

_SELECT_FIELDS = "id, language_code, term, translation_pt, example_sentence, frequency_rank"


def get_all_words() -> list[dict]:
    with SessionLocal() as db:
        rows = db.execute(text(f"SELECT {_SELECT_FIELDS} FROM words ORDER BY frequency_rank")).mappings().all()
        return [dict(row) for row in rows]


def get_word_by_id(word_id: int) -> dict | None:
    with SessionLocal() as db:
        row = db.execute(
            text(f"SELECT {_SELECT_FIELDS} FROM words WHERE id = :id"),
            {"id": word_id},
        ).mappings().first()
        return dict(row) if row else None


def get_unseen_words(user_id: int, limit: int) -> list[dict]:
    """Palavras (menor frequency_rank primeiro) que o usuário ainda não tem em user_word_progress,
    de nenhum status — nem conhecida no nivelamento, nem já vista numa lição anterior."""
    with SessionLocal() as db:
        rows = db.execute(
            text(
                f"""
                SELECT {_SELECT_FIELDS} FROM words w
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_word_progress p
                    WHERE p.word_id = w.id AND p.user_id = :user_id
                )
                ORDER BY w.frequency_rank
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]


def get_words_by_ids(word_ids: list[int]) -> list[dict]:
    if not word_ids:
        return []
    with SessionLocal() as db:
        rows = db.execute(
            text(f"SELECT {_SELECT_FIELDS} FROM words WHERE id = ANY(:ids) ORDER BY frequency_rank"),
            {"ids": word_ids},
        ).mappings().all()
        return [dict(row) for row in rows]


def get_next_untested_word(user_id: int, exclude_ids: list[int]) -> dict | None:
    """Próxima palavra (menor frequency_rank) que o usuário ainda não tem em user_word_progress
    e que não foi testada ainda nesta sessão de nivelamento (exclude_ids)."""
    with SessionLocal() as db:
        row = db.execute(
            text(
                f"""
                SELECT {_SELECT_FIELDS} FROM words w
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_word_progress p
                    WHERE p.word_id = w.id AND p.user_id = :user_id
                )
                AND w.id != ALL(:exclude_ids)
                ORDER BY w.frequency_rank
                LIMIT 1
                """
            ),
            {"user_id": user_id, "exclude_ids": exclude_ids or [0]},
        ).mappings().first()
        return dict(row) if row else None
