"""Copy data from a local SQLite DB to a Postgres DB (e.g. Supabase) using SQLAlchemy.

Usage:
  - Ensure `DATABASE_URL` points to the target Postgres DB (export DATABASE_URL)
  - Optionally set SOURCE_SQLITE (path to sqlite file). Default: repository `data.sqlite3`.
  - Run: python scripts/migrate_sqlite_to_postgres.py

Notes:
  - This script will create tables on the target DB using the application's models, then copy rows
    table-by-table attempting to preserve primary keys. It attempts to order tables to satisfy
    foreign-key dependencies.
  - After copying it will try to set Postgres sequences (serial) to the max(id) for tables with
    a single integer PK named `id`.
  - Test in a staging Supabase project before production.
"""
from __future__ import annotations

import os
import sys
import logging
from typing import Dict, List, Set

from sqlalchemy import create_engine, MetaData, Table, select, insert, text
from sqlalchemy.engine import Engine

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("migrate")


def topological_sort_tables(metadata: MetaData) -> List[Table]:
    """Return tables in an order that respects foreign key dependencies (simple topo sort)."""
    deps: Dict[str, Set[str]] = {}
    tables = {t.name: t for t in metadata.sorted_tables}
    for name, table in tables.items():
        refs = set()
        for fk in table.foreign_keys:
            refs.add(fk.column.table.name)
        deps[name] = refs

    ordered: List[Table] = []
    while deps:
        # pick tables with no dependencies
        ready = [n for n, d in deps.items() if not d]
        if not ready:
            # circular or unresolved; just append remaining
            logger.warning("Circular dependency detected or unresolved FKs: %s", deps.keys())
            for n in list(deps.keys()):
                ordered.append(tables[n])
                deps.pop(n)
            break
        for n in ready:
            ordered.append(tables[n])
            deps.pop(n)
            for other in deps:
                deps[other].discard(n)

    return ordered


def copy_table(source: Engine, target: Engine, table: Table) -> int:
    s_conn = source.connect()
    t_conn = target.connect()
    trans = t_conn.begin()
    try:
        rows = s_conn.execute(select(table)).mappings().all()
        if not rows:
            logger.info("Skipping empty table %s", table.name)
            trans.commit()
            return 0

        # Insert rows in chunks
        chunk_size = 500
        total = 0
        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            # convert Mapping objects to dicts
            dicts = [dict(r) for r in chunk]
            t_conn.execute(insert(table).prefix_with("/* migrate */"), dicts)
            total += len(dicts)

        trans.commit()
        logger.info("Copied %d rows into %s", total, table.name)
        return total
    except Exception:
        trans.rollback()
        logger.exception("Failed to copy table %s", table.name)
        raise
    finally:
        s_conn.close()
        t_conn.close()


def set_postgres_sequence(target: Engine, table_name: str, pk_name: str = "id") -> None:
    # Set sequence to max(id) if sequence exists
    try:
        with target.connect() as conn:
            # find the sequence for this serial column
            sql = text(
                "SELECT pg_get_serial_sequence(:table, :pk) as seq"
            )
            seq = conn.execute(sql, {"table": table_name, "pk": pk_name}).scalar()
            if not seq:
                return
            max_sql = text(f"SELECT coalesce(max({pk_name}), 0) FROM \"{table_name}\"")
            maxv = conn.execute(max_sql).scalar() or 0
            set_sql = text(f"SELECT setval(:seq, :val, true)")
            conn.execute(set_sql, {"seq": seq, "val": int(maxv)})
            logger.info("Set sequence %s to %s", seq, maxv)
    except Exception:
        logger.exception("Failed to set sequence for %s", table_name)


def main() -> None:
    sqlite_path = os.environ.get("SOURCE_SQLITE") or os.path.join(ROOT, "data.sqlite3")
    if not os.path.exists(sqlite_path):
        logger.error("Source SQLite not found at %s", sqlite_path)
        return

    dest_url = os.environ.get("DATABASE_URL")
    if not dest_url:
        logger.error("Please set DATABASE_URL to your target Postgres (Supabase) database URL")
        return

    source_url = f"sqlite:///{sqlite_path}"
    logger.info("Source: %s", source_url)
    logger.info("Destination: %s", dest_url)

    source_engine = create_engine(source_url, connect_args={"check_same_thread": False})
    target_engine = create_engine(dest_url)

    # Ensure models/tables exist on target
    try:
        # Import application models so Base metadata is populated
        import server.models  # noqa: F401
        import server.db as _db  # noqa: F401

        _db.Base.metadata.create_all(bind=target_engine)
    except Exception:
        logger.exception("Failed to create tables on target DB via models metadata")
        raise

    # Reflect source metadata (actual tables)
    src_meta = MetaData()
    src_meta.reflect(bind=source_engine)

    ordered = topological_sort_tables(src_meta)

    total_rows = 0
    for tbl in ordered:
        try:
            copied = copy_table(source_engine, target_engine, tbl)
            total_rows += copied
            # attempt to set Postgres sequence if PK is `id` integer
            if "id" in [c.name for c in tbl.primary_key.columns]:
                set_postgres_sequence(target_engine, tbl.name, "id")
        except Exception:
            logger.exception("Error copying table %s; aborting", tbl.name)
            raise

    logger.info("Migration complete. Total rows copied: %d", total_rows)


if __name__ == "__main__":
    main()
