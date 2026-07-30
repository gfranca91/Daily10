"""Insere o JSON de seed (app/data/seed_words_es.json) na tabela `words` do Neon.
Idempotente: usa ON CONFLICT (language_code, term) DO NOTHING.

Uso: ./venv/Scripts/python.exe scripts/seed_words.py
"""

import json
from pathlib import Path

from sqlalchemy import text

from app.db import engine
from app.services.cefr import level_for_rank
from app.services.cognates import is_cognate

SEED_PATH = Path(__file__).resolve().parent.parent / "app" / "data" / "seed_words_es.json"

INSERT_SQL = text(
    """
    INSERT INTO words (language_code, term, translation_pt, example_sentence, frequency_rank, cefr_level, is_cognate)
    VALUES (:language_code, :term, :translation_pt, :example_sentence, :frequency_rank, :cefr_level, :is_cognate)
    ON CONFLICT (language_code, term) DO NOTHING
    """
)

if __name__ == "__main__":
    words = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    with engine.begin() as conn:
        for word in words:
            conn.execute(
                INSERT_SQL,
                {
                    "language_code": word["language_code"],
                    "term": word["term"],
                    "translation_pt": word["translation_pt"],
                    "example_sentence": word["example_sentence"],
                    "frequency_rank": word["frequency_rank"],
                    "cefr_level": level_for_rank(word["frequency_rank"]),
                    "is_cognate": is_cognate(word["term"], word["translation_pt"]),
                },
            )

    print(f"{len(words)} palavras processadas (inseridas ou já existentes).")
