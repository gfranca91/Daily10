"""Reseta o teste de nivelamento de todo mundo, pra refazer com a exclusão de
cognatos já aplicada (nivelamentos antigos podiam inflar o nível com palavras
"de graça"). Mantém `declared_level` e todo o progresso de lição/exercício —
só força passar pelo teste de novo no próximo login.

Uso: PYTHONPATH=. ./venv/Scripts/python.exe scripts/reset_placement_tests.py
"""

from sqlalchemy import text

from app.db import engine

if __name__ == "__main__":
    with engine.begin() as conn:
        result = conn.execute(text("UPDATE users SET placement_test_done = false"))
        print(f"{result.rowcount} contas resetadas — vão refazer o nivelamento no próximo login.")
