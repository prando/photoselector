"""Apply numbered SQL migrations and record schema_version."""

from __future__ import annotations

import sqlite3
from importlib import resources
from importlib.resources.abc import Traversable


def migrate(conn: sqlite3.Connection) -> None:
    """Apply pending migrations in lexical order."""
    current = schema_version(conn)
    for item in _migration_files():
        version = int(item.name.split("_", 1)[0])
        if version <= current:
            continue
        _apply(conn, item, version)
        current = version


def schema_version(conn: sqlite3.Connection) -> int:
    """Return the stored schema version, or 0 if the table is missing."""
    try:
        row = conn.execute(
            "SELECT value FROM project_data WHERE key = 'schema_version'"
        ).fetchone()
    except sqlite3.OperationalError:
        return 0
    return int(row[0]) if row else 0


def _apply(conn: sqlite3.Connection, item: Traversable, version: int) -> None:
    conn.executescript(item.read_text(encoding="utf-8"))
    conn.execute(
        "INSERT OR REPLACE INTO project_data(key, value) VALUES ('schema_version', ?)",
        (str(version),),
    )


def _migration_files() -> list[Traversable]:
    root = resources.files("photoselector.catalog.migrations")
    items = [item for item in root.iterdir() if item.name.endswith(".sql")]
    return sorted(items, key=lambda item: item.name)
