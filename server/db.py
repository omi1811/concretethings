from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase


# Get database URL from environment or use SQLite default
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DB_PATH = Path(__file__).resolve().parent.parent / "data.sqlite3"
    DATABASE_URL = f"sqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    pass


# Configure engine based on database type
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {"check_same_thread": False}
elif DATABASE_URL.startswith('postgresql'):
    # Force IPv4 for Supabase connection (Render doesn't support IPv6)
    connect_args = {
        "connect_timeout": 10,
        "options": "-c search_path=public"
    }

# If using PostgreSQL with Supabase, ensure we use pooler connection string
# Replace direct connection with pooler (IPv4 only)
database_url = DATABASE_URL
if 'supabase.co' in DATABASE_URL and 'pooler' not in DATABASE_URL:
    # Use IPv4 pooler connection
    database_url = DATABASE_URL.replace(
        'db.lsqvxfaonbvqvlwrhsby.supabase.co',
        'aws-0-ap-south-1.pooler.supabase.com'
    ).replace(':5432', ':6543')

engine = create_engine(
    database_url, 
    echo=False, 
    connect_args=connect_args,
    pool_pre_ping=True  # Verify connections before using
)
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


@contextmanager
def session_scope() -> Iterator[scoped_session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from . import models  # noqa: F401 - ensure models are imported

    Base.metadata.create_all(bind=engine)
