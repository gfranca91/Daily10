"""Migração única: adiciona `words.is_cognate` e classifica as palavras existentes.

Idempotente: ALTER TABLE ... ADD COLUMN IF NOT EXISTS; reclassifica todas as
linhas toda vez que roda (barato, só um SequenceMatcher em memória).

Uso: PYTHONPATH=. ./venv/Scripts/python.exe scripts/migrate_add_cognates.py
"""

from sqlalchemy import text

from app.db import engine
from app.services.cognates import is_cognate

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE words ADD COLUMN IF NOT EXISTS is_cognate BOOLEAN NOT NULL DEFAULT false"))

        rows = conn.execute(text("SELECT id, term, translation_pt FROM words")).all()

        cognate_count = 0
        for word_id, term, translation_pt in rows:
            cognate = is_cognate(term, translation_pt)
            if cognate:
                cognate_count += 1
            conn.execute(
                text("UPDATE words SET is_cognate = :is_cognate WHERE id = :id"),
                {"is_cognate": cognate, "id": word_id},
            )

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_words_is_cognate ON words (is_cognate)"))

    print(f"{len(rows)} palavras classificadas, {cognate_count} marcadas como cognatas.")
