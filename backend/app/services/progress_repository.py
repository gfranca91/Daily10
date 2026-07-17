from sqlalchemy import text

from app.db import SessionLocal
from app.services.srs import apply_sm2


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


def get_due_word_ids(user_id: int) -> list[int]:
    """Palavras com revisão devida hoje (novas de hoje ou agendadas pelo SM-2), ordenadas
    pela mais atrasada primeiro. Exclui palavras marcadas conhecidas no nivelamento."""
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT word_id FROM user_word_progress
                WHERE user_id = :user_id
                AND status IN ('learning', 'review')
                AND due_date <= CURRENT_DATE
                ORDER BY due_date
                """
            ),
            {"user_id": user_id},
        ).all()
        return [row[0] for row in rows]


def record_review(user_id: int, word_id: int, correct: bool) -> None:
    """Aplica o SM-2 depois de uma resposta no exercício de fixação/revisão."""
    with SessionLocal() as db:
        row = db.execute(
            text(
                """
                SELECT repetitions, easiness_factor, interval_days
                FROM user_word_progress
                WHERE user_id = :user_id AND word_id = :word_id
                """
            ),
            {"user_id": user_id, "word_id": word_id},
        ).first()
        if row is None:
            return

        result = apply_sm2(
            repetitions=row[0],
            easiness_factor=float(row[1]),
            interval_days=row[2],
            correct=correct,
        )

        db.execute(
            text(
                """
                UPDATE user_word_progress
                SET status = 'review',
                    repetitions = :repetitions,
                    easiness_factor = :easiness_factor,
                    interval_days = :interval_days,
                    due_date = :due_date,
                    last_reviewed_at = now()
                WHERE user_id = :user_id AND word_id = :word_id
                """
            ),
            {
                "user_id": user_id,
                "word_id": word_id,
                "repetitions": result["repetitions"],
                "easiness_factor": result["easiness_factor"],
                "interval_days": result["interval_days"],
                "due_date": result["due_date"],
            },
        )
        db.commit()
