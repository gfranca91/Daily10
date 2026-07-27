"""Migração única: adiciona níveis CEFR (A1-C2) em `words` e `users`.

- `words.cefr_level`: derivado do `frequency_rank` atual, em faixas (aproximação,
  não é uma classificação linguística oficial).
- `users.declared_level` / `current_level` / `placement_test_done`: suporte ao
  novo fluxo de cadastro com escolha de nível + teste de nivelamento adaptativo.

Idempotente: usa IF NOT EXISTS / verifica antes de aplicar cada passo.

Uso: PYTHONPATH=. ./venv/Scripts/python.exe scripts/migrate_add_levels.py
"""

from sqlalchemy import text

from app.db import engine

# Faixas de frequency_rank -> nível CEFR. Ajustadas conforme o vocabulário cresce.
LEVEL_BANDS = [
    (1, 120, "A1"),
    (121, 260, "A2"),
    (261, 420, "B1"),
    (421, 10_000, "B2"),  # cauda aberta; lotes futuros de B2/C1/C2 vão sobrescrever faixas específicas
]

if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS declared_level TEXT"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS current_level TEXT"))
        conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS placement_test_done BOOLEAN NOT NULL DEFAULT false")
        )
        conn.execute(text("ALTER TABLE words ADD COLUMN IF NOT EXISTS cefr_level TEXT"))

        for low, high, level in LEVEL_BANDS:
            result = conn.execute(
                text(
                    """
                    UPDATE words SET cefr_level = :level
                    WHERE frequency_rank BETWEEN :low AND :high AND cefr_level IS NULL
                    """
                ),
                {"level": level, "low": low, "high": high},
            )
            print(f"{level} (rank {low}-{high}): {result.rowcount} palavras atualizadas")

        conn.execute(text("ALTER TABLE words ALTER COLUMN cefr_level SET NOT NULL"))

        conn.execute(
            text(
                """
                DO $$ BEGIN
                    ALTER TABLE words ADD CONSTRAINT words_cefr_level_check
                        CHECK (cefr_level IN ('A1','A2','B1','B2','C1','C2'));
                EXCEPTION WHEN duplicate_object THEN NULL;
                END $$;
                """
            )
        )
        conn.execute(
            text(
                """
                DO $$ BEGIN
                    ALTER TABLE users ADD CONSTRAINT users_declared_level_check
                        CHECK (declared_level IN ('A1','A2','B1','B2','C1','C2'));
                EXCEPTION WHEN duplicate_object THEN NULL;
                END $$;
                """
            )
        )
        conn.execute(
            text(
                """
                DO $$ BEGIN
                    ALTER TABLE users ADD CONSTRAINT users_current_level_check
                        CHECK (current_level IN ('A1','A2','B1','B2','C1','C2'));
                EXCEPTION WHEN duplicate_object THEN NULL;
                END $$;
                """
            )
        )
        conn.execute(
            text("CREATE INDEX IF NOT EXISTS idx_words_language_level ON words (language_code, cefr_level, frequency_rank)")
        )

    print("Migração concluída.")
