from sqlalchemy import text

from app.db import SessionLocal


def mark_known_at_onboarding(user_id: int, word_id: int) -> None:
    with SessionLocal() as db:
        db.execute(
            text(
                """
                INSERT INTO user_word_progress (user_id, word_id, status)
                VALUES (:user_id, :word_id, 'known_at_onboarding')
                ON CONFLICT (user_id, word_id) DO NOTHING
                """
            ),
            {"user_id": user_id, "word_id": word_id},
        )
        db.commit()


def get_today_lesson_word_ids(user_id: int) -> list[int]:
    """Palavras já atribuídas como lição HOJE (status='learning', criadas hoje). Torna
    GET /lessons/today idempotente: recarregar a página não sorteia palavras novas."""
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT word_id FROM user_word_progress
                WHERE user_id = :user_id
                AND status = 'learning'
                AND created_at::date = CURRENT_DATE
                """
            ),
            {"user_id": user_id},
        ).all()
        return [row[0] for row in rows]


def assign_daily_lesson(user_id: int, word_ids: list[int]) -> None:
    """due_date = hoje: a palavra já entra "devida" pro exercício de fixação do mesmo dia,
    que funciona como a primeira revisão SM-2 dela."""
    if not word_ids:
        return
    with SessionLocal() as db:
        for word_id in word_ids:
            db.execute(
                text(
                    """
                    INSERT INTO user_word_progress (user_id, word_id, status, due_date)
                    VALUES (:user_id, :word_id, 'learning', CURRENT_DATE)
                    ON CONFLICT (user_id, word_id) DO NOTHING
                    """
                ),
                {"user_id": user_id, "word_id": word_id},
            )
        db.commit()


def get_review_due_word_ids(user_id: int) -> list[int]:
    """Palavras de dias anteriores com revisão devida hoje (SM-2) — exclui a lição de HOJE,
    que tem sua própria fase de exercício separada. Cobre tanto quem já foi revisado antes
    (status='review') quanto quem ficou sem revisar num dia anterior (status='learning' atrasado)."""
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT word_id FROM user_word_progress
                WHERE user_id = :user_id
                AND status IN ('learning', 'review')
                AND due_date <= CURRENT_DATE
                AND created_at::date < CURRENT_DATE
                ORDER BY due_date
                """
            ),
            {"user_id": user_id},
        ).all()
        return [row[0] for row in rows]


