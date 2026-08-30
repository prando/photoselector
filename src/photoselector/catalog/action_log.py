"""500-row undo/redo ring buffer."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

RING = 500


def log_action(conn: sqlite3.Connection, op: str, payload: dict[str, Any]) -> None:
    """Append one action, wrapping at RING and advancing the undo cursor."""
    seq = _next_seq(conn) % RING
    conn.execute(
        """
        INSERT INTO action_log (seq, op, payload, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(seq) DO UPDATE SET
            op = excluded.op,
            payload = excluded.payload,
            created_at = excluded.created_at
        """,
        (seq, op, json.dumps(payload), _now()),
    )
    height = min(_logical_height(conn), RING)
    _put(conn, "undo_cursor", str(height))


def undo_cursor(conn: sqlite3.Connection) -> int:
    """Return the clamped undo cursor."""
    return clamp_cursor(conn)


def clamp_cursor(conn: sqlite3.Connection) -> int:
    """Force undo_cursor into [0, min(count, RING)]."""
    raw = int(_get(conn, "undo_cursor", "0"))
    height = min(_count(conn), RING)
    cur = max(0, min(raw, height))
    if cur != raw:
        _put(conn, "undo_cursor", str(cur))
    return cur


def _next_seq(conn: sqlite3.Connection) -> int:
    n = int(_get(conn, "action_seq", "0"))
    _put(conn, "action_seq", str(n + 1))
    return n


def _logical_height(conn: sqlite3.Connection) -> int:
    return int(_get(conn, "action_seq", "0"))


def _count(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) FROM action_log").fetchone()
    return int(row[0]) if row else 0


def _get(conn: sqlite3.Connection, key: str, default: str) -> str:
    row = conn.execute(
        "SELECT value FROM project_data WHERE key = ?", (key,)
    ).fetchone()
    return str(row[0]) if row else default


def _put(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO project_data(key, value) VALUES (?, ?)",
        (key, value),
    )


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
