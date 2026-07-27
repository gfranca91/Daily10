from sqlalchemy import text

from app.db import SessionLocal
from app.services.srs import apply_sm2


def get_practice_exercises_for_words(word_ids: list[int]) -> list[dict]:
    """Uma frase de exercício (com as 4 opções) para cada palavra em word_ids que já
    tem frase cadastrada. Palavras sem frase ainda são simplesmente puladas."""
    if not word_ids:
        return []

    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT ps.id AS sentence_id, ps.sentence_template,
                       po.option_word_id, ow.term AS option_term
                FROM practice_sentences ps
                JOIN practice_options po ON po.practice_sentence_id = ps.id
                JOIN words ow ON ow.id = po.option_word_id
                WHERE ps.word_id = ANY(:word_ids)
                ORDER BY ps.id
                """
            ),
            {"word_ids": word_ids},
        ).mappings().all()

    exercises_by_sentence: dict[int, dict] = {}
    for row in rows:
        sentence_id = row["sentence_id"]
        if sentence_id not in exercises_by_sentence:
            exercises_by_sentence[sentence_id] = {
                "sentence_id": sentence_id,
                "sentence_template": row["sentence_template"],
                "options": [],
            }
        exercises_by_sentence[sentence_id]["options"].append(
            {"word_id": row["option_word_id"], "term": row["option_term"]}
        )

    return list(exercises_by_sentence.values())


def check_practice_answer(user_id: int, sentence_id: int, option_word_id: int) -> dict | None:
    """Confere a resposta E já aplica o SM-2, tudo numa única conexão/transação
    (antes eram 3 idas ao banco separadas — cada uma paga a latência até o Neon)."""
    with SessionLocal() as db:
        option_row = db.execute(
            text(
                """
                SELECT po.is_correct, correct_word.term AS correct_term, ps.word_id
                FROM practice_options po
                JOIN practice_sentences ps ON ps.id = po.practice_sentence_id
                JOIN words correct_word ON correct_word.id = ps.word_id
                WHERE po.practice_sentence_id = :sentence_id AND po.option_word_id = :option_word_id
                """
            ),
            {"sentence_id": sentence_id, "option_word_id": option_word_id},
        ).mappings().first()

        if option_row is None:
            return None

        progress_row = db.execute(
            text(
                """
                SELECT repetitions, easiness_factor, interval_days
                FROM user_word_progress
                WHERE user_id = :user_id AND word_id = :word_id
                """
            ),
            {"user_id": user_id, "word_id": option_row["word_id"]},
        ).first()

        if progress_row is not None:
            result = apply_sm2(
                repetitions=progress_row[0],
                easiness_factor=float(progress_row[1]),
                interval_days=progress_row[2],
                correct=option_row["is_correct"],
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
                    "word_id": option_row["word_id"],
                    "repetitions": result["repetitions"],
                    "easiness_factor": result["easiness_factor"],
                    "interval_days": result["interval_days"],
                    "due_date": result["due_date"],
                },
            )
            db.commit()

        return dict(option_row)
