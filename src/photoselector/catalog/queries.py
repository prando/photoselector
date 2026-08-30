"""Read-only catalog queries."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from photoselector.catalog.models import Format, Rating


@dataclass(frozen=True)
class PhotoRecord:
    """A photo plus sparse cull state."""

    id: int
    path: str
    filename: str
    mtime_ns: int
    size_bytes: int
    fmt: Format
    taken_at: str | None
    rating: Rating | None
    stars: int | None
    color: str | None
    rotate_quarters: int


_SQL = """
SELECT
    p.id, p.path, p.filename, p.mtime_ns, p.size_bytes, p.format,
    p.taken_at, s.rating, p.stars, p.color, p.rotate_quarters
FROM photo p
LEFT JOIN selection s ON s.photo_id = p.id
ORDER BY COALESCE(p.taken_at, p.filename), p.filename
"""


def load_photos(conn: sqlite3.Connection) -> list[PhotoRecord]:
    """All photos with optional selection row."""
    rows = conn.execute(_SQL).fetchall()
    return [_row(row) for row in rows]


def _row(row: sqlite3.Row) -> PhotoRecord:
    raw = row["rating"]
    rating = Rating(raw) if raw else None
    return PhotoRecord(
        id=int(row["id"]),
        path=str(row["path"]),
        filename=str(row["filename"]),
        mtime_ns=int(row["mtime_ns"]),
        size_bytes=int(row["size_bytes"]),
        fmt=row["format"],
        taken_at=row["taken_at"],
        rating=rating,
        stars=row["stars"],
        color=row["color"],
        rotate_quarters=int(row["rotate_quarters"]),
    )
