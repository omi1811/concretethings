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
    """
    Ensure ORM models are registered so SQLAlchemy can create tables.

    We attempt an absolute import of `server.models` first (works in normal package mode).
    If that fails (odd execution mode), we try a relative import as a fallback.
    This import is done inside the function to avoid package-context issues and
    to reduce circular-import problems.
    """
    import importlib

    # Try multiple import strategies to be resilient to different invocation modes
    excs = {}
    # 1) Preferred absolute import (package mode)
    try:
        importlib.import_module("server.models")  # noqa: F401
        models_imported = True
    except Exception as e:
        excs['server.models'] = e
        models_imported = False

    # 2) Try bare module import (when running with PYTHONPATH set)
    if not models_imported:
        try:
            importlib.import_module("models")  # noqa: F401
            models_imported = True
        except Exception as e:
            excs['models'] = e

    # 3) As a last resort, attempt to load the file directly by path
    if not models_imported:
        try:
            models_path = Path(__file__).resolve().parent / "models.py"
            if models_path.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location("server.models", str(models_path))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore[attr-defined]
                # Register in sys.modules so SQLAlchemy can find the classes
                import sys
                sys.modules["server.models"] = module
                models_imported = True
            else:
                excs['file'] = FileNotFoundError(f"{models_path} not found")
        except Exception as e:
            excs['file'] = e

    if not models_imported:
        # Build helpful error message including all attempts
        messages = [f"Tried import '{k}' and got: {v!r}" for k, v in excs.items()]
        raise ImportError(
            "Failed to import models for database initialization. "
            "Tried multiple import strategies (package absolute, bare module, direct file).\n\n"
            + "\n".join(messages)
            + "\n\nEnsure 'server/__init__.py' exists and run Flask from the project root "
            "with FLASK_APP set to 'server.app:app' (or use 'flask --app server.app run')."
        )

    # Now create tables after the models are imported and registered on Base
    Base.metadata.create_all(bind=engine)



# Compatibility layer for db.session pattern (used in some blueprints)
class _DBSession:
    """
    Compatibility wrapper to provide db.session interface for legacy code.
    Maps to the scoped_session SessionLocal.
    """
    @property
    def query(self):
        return SessionLocal().query
    
    def add(self, instance):
        return SessionLocal().add(instance)
    
    def commit(self):
        return SessionLocal().commit()
    
    def rollback(self):
        return SessionLocal().rollback()
    
    def flush(self):
        return SessionLocal().flush()
    
    def close(self):
        return SessionLocal().close()
    
    def remove(self):
        return SessionLocal.remove()


# Create compatibility db object
class _DB:
    session = _DBSession()


db = _DB()
