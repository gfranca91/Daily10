import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

_raw_url = os.environ["DATABASE_URL"]
_engine_url = _raw_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(_engine_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
