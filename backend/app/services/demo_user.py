from sqlalchemy import text

from app.db import SessionLocal

DEMO_USER_EMAIL = "demo@daily10.local"


def get_demo_user_id() -> int:
    """TEMPORÁRIO: não há login ainda, todo mundo usa este único usuário fixo no Neon."""
    with SessionLocal() as db:
        row = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": DEMO_USER_EMAIL}).first()
        if row:
            return row[0]

        result = db.execute(
            text("INSERT INTO users (email, password_hash) VALUES (:email, 'demo') RETURNING id"),
            {"email": DEMO_USER_EMAIL},
        )
        db.commit()
        return result.scalar()
