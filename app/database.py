"""Database session management for the vending machine service."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings


def _sqlite_connect_args(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        # Ensure parent directory exists when using SQLite files.
        database_path = database_url.split("///")[-1]
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        return {"check_same_thread": False}
    return {}


database_url = settings.database_url
engine = create_engine(database_url, connect_args=_sqlite_connect_args(database_url))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()


def init_db() -> None:
    """Create database tables on startup."""

    from . import models  # noqa: F401 - ensures models are imported for metadata

    Base.metadata.create_all(bind=engine)


def get_session() -> Iterator[Session]:
    """Provide a transactional scope for database operations."""

    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
