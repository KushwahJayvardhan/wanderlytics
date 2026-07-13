"""
database.py

SQLAlchemy engine/session setup. Reads the connection string from the
DATABASE_URL environment variable so the same code works locally
(SQLite/Postgres) and in production (Render/Railway Postgres).
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Defaults to a local SQLite file so the project runs out of the box
# with zero setup. Swap DATABASE_URL to a Postgres URL for production,
# e.g. postgresql://user:password@host:5432/tripscope
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tripscope.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
