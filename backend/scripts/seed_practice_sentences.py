"""Insere o JSON de frases de exercício (app/data/practice_sentences_es.json) no Neon:
uma linha em `practice_sentences` por palavra, mais 4 opções em `practice_options`
(a correta + 3 distratores aleatórios de outras palavras do mesmo idioma).

Idempotente: pula palavras que já têm alguma frase cadastrada.

Uso: PYTHONPATH=. ./venv/Scripts/python.exe scripts/seed_practice_sentences.py
"""

import json
import random
from pathlib import Path

from sqlalchemy import text

from app.db import engine

SEED_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "practice_sentences_es.json"
NUM_DISTRACTORS = 3

if __name__ == "__main__":
    entries = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    inserted = 0
    skipped = 0

    with engine.begin() as conn:
        for entry in entries:
            word_row = conn.execute(
                text("SELECT id FROM words WHERE language_code = 'es' AND term = :term"),
                {"term": entry["term"]},
            ).first()
            if word_row is None:
                print(f"AVISO: palavra '{entry['term']}' não encontrada em words, pulando.")
                continue
            word_id = word_row[0]

            existing = conn.execute(
                text("SELECT 1 FROM practice_sentences WHERE word_id = :word_id"),
                {"word_id": word_id},
            ).first()
            if existing:
                skipped += 1
                continue

            sentence_id = conn.execute(
                text(
                    """
                    INSERT INTO practice_sentences (word_id, sentence_template)
                    VALUES (:word_id, :sentence_template)
                    RETURNING id
                    """
                ),
                {"word_id": word_id, "sentence_template": entry["sentence_template"]},
            ).scalar()

            distractor_rows = conn.execute(
                text(
                    """
                    SELECT id FROM words
                    WHERE language_code = 'es' AND id != :word_id
                    ORDER BY random()
                    LIMIT :n
                    """
                ),
                {"word_id": word_id, "n": NUM_DISTRACTORS},
            ).all()

            option_word_ids = [word_id] + [row[0] for row in distractor_rows]
            random.shuffle(option_word_ids)

            for option_word_id in option_word_ids:
                conn.execute(
                    text(
                        """
                        INSERT INTO practice_options (practice_sentence_id, option_word_id, is_correct)
                        VALUES (:sentence_id, :option_word_id, :is_correct)
                        """
                    ),
                    {
                        "sentence_id": sentence_id,
                        "option_word_id": option_word_id,
                        "is_correct": option_word_id == word_id,
                    },
                )

            inserted += 1

    print(f"{inserted} frases inseridas, {skipped} já existiam (puladas).")
