"""Read-write and read-only SQLite connections."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_PRAGMAS = (
    "PRAGMA journal_mode=WAL",
    "PRAGMA synchronous=NORMAL",
    "PRAGMA busy_timeout=5000",
    "PRAGMA foreign_keys=ON",
)


def open_writer(path: Path) -> sqlite3.Connection:
    """Open the sole read-write connection for a catalog file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)
    return conn


def open_reader(path: Path) -> sqlite3.Connection:
    """Open a read-only connection. The catalog file must already exist."""
    uri = f"file:{path.as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    for pragma in _PRAGMAS:
        conn.execute(pragma)
