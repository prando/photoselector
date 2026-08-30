"""Photo and selection mutations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Literal

Format = Literal["jpeg", "png", "heic", "raw"]


class Rating(Enum):
    """Cull state stored in the sparse selection table."""

    PICK = "pick"
    REJECT = "reject"


@dataclass(frozen=True)
class Photo:
    """A catalogued image file."""

    path: str
    filename: str
    mtime_ns: int
    size_bytes: int
    fmt: Format
    taken_at: str | None = None
    orientation: int = 1


UPSERT_SQL = """
INSERT INTO photo (
    path, filename, mtime_ns, size_bytes, taken_at,
    width, height, orientation, format, phash, group_id,
    stars, color, rotate_quarters, scanned_at
) VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?, NULL, NULL, NULL, NULL, 0, ?)
ON CONFLICT(path) DO UPDATE SET
    filename = excluded.filename,
    mtime_ns = excluded.mtime_ns,
    size_bytes = excluded.size_bytes,
    format = excluded.format,
    scanned_at = excluded.scanned_at
"""

RATE_SQL = """
INSERT INTO selection (photo_id, rating, updated_at) VALUES (?, ?, ?)
ON CONFLICT(photo_id) DO UPDATE SET
    rating = excluded.rating,
    updated_at = excluded.updated_at
"""


def upsert_photo(conn: sqlite3.Connection, photo: Photo) -> int:
    """Insert or refresh a photo row. Returns the row id."""
    conn.execute(
        UPSERT_SQL,
        (
            photo.path,
            photo.filename,
            photo.mtime_ns,
            photo.size_bytes,
            photo.taken_at,
            photo.orientation,
            photo.fmt,
            utc_now(),
        ),
    )
    row = conn.execute("SELECT id FROM photo WHERE path = ?", (photo.path,)).fetchone()
    if row is None:
        raise RuntimeError(f"photo missing after upsert: {photo.path}")
    return int(row[0])


def set_rating(conn: sqlite3.Connection, photo_id: int, rating: Rating) -> None:
    """Create or replace the sparse selection row."""
    conn.execute(RATE_SQL, (photo_id, rating.value, utc_now()))


def clear_rating(conn: sqlite3.Connection, photo_id: int) -> None:
    """Delete the selection row (unrated)."""
    conn.execute("DELETE FROM selection WHERE photo_id = ?", (photo_id,))


def photo_count(conn: sqlite3.Connection) -> int:
    """Return the number of photo rows."""
    row = conn.execute("SELECT COUNT(*) FROM photo").fetchone()
    return int(row[0]) if row else 0


def utc_now() -> str:
    """UTC timestamp used for scanned_at / updated_at."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()
