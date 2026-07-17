from sqlalchemy import text

from app.db import SessionLocal


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


def check_practice_answer(sentence_id: int, option_word_id: int) -> dict | None:
    with SessionLocal() as db:
        row = db.execute(
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
        return dict(row) if row else None
