"""
Database session management utilities.
"""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from .base import SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """Create all database tables."""
    from .base import Base, engine

    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    from .base import Base, engine

    Base.metadata.drop_all(bind=engine)
