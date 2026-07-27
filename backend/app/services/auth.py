import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Header, HTTPException
from sqlalchemy import text

from app.db import SessionLocal

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_DAYS = 30


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRES_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_user_by_email(email: str) -> dict | None:
    with SessionLocal() as db:
        row = db.execute(
            text("SELECT id, email, password_hash FROM users WHERE email = :email"),
            {"email": email},
        ).mappings().first()
        return dict(row) if row else None


def create_user(email: str, password: str, declared_level: str) -> int:
    with SessionLocal() as db:
        result = db.execute(
            text(
                """
                INSERT INTO users (email, password_hash, declared_level, current_level)
                VALUES (:email, :password_hash, :declared_level, :declared_level)
                RETURNING id
                """
            ),
            {"email": email, "password_hash": hash_password(password), "declared_level": declared_level},
        )
        db.commit()
        return result.scalar()


def get_user_state(user_id: int) -> dict | None:
    with SessionLocal() as db:
        row = db.execute(
            text(
                "SELECT declared_level, current_level, placement_test_done FROM users WHERE id = :user_id"
            ),
            {"user_id": user_id},
        ).mappings().first()
        return dict(row) if row else None


def set_declared_level(user_id: int, declared_level: str) -> None:
    """Pra contas criadas antes do sistema de níveis existir (sem declared_level ainda)."""
    with SessionLocal() as db:
        db.execute(
            text("UPDATE users SET declared_level = :level WHERE id = :user_id"),
            {"level": declared_level, "user_id": user_id},
        )
        db.commit()


def complete_placement(user_id: int, confirmed_level: str) -> None:
    with SessionLocal() as db:
        db.execute(
            text(
                """
                UPDATE users SET current_level = :level, placement_test_done = true
                WHERE id = :user_id
                """
            ),
            {"level": confirmed_level, "user_id": user_id},
        )
        db.commit()


def get_current_user_id(authorization: str | None = Header(default=None)) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autenticado")

    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return int(payload["sub"])
