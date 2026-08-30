"""Rate / unrate and undo through the writer queue."""

from __future__ import annotations

from typing import Any

from photoselector.catalog.action_log import RING
from photoselector.catalog.models import RATE_SQL, Rating, utc_now
from photoselector.catalog.writer import Writer

CLEAR_SQL = "DELETE FROM selection WHERE photo_id = ?"
LOG_SQL = """
INSERT INTO action_log (seq, op, payload, created_at)
VALUES (?, ?, ?, ?)
ON CONFLICT(seq) DO UPDATE SET
    op = excluded.op,
    payload = excluded.payload,
    created_at = excluded.created_at
"""
PUT_SQL = "INSERT OR REPLACE INTO project_data(key, value) VALUES (?, ?)"


def enqueue_rating(
    writer: Writer,
    photo_id: int,
    rating: Rating | None,
    *,
    seq: int,
) -> None:
    """Queue persist + action_log for one cull mutation."""
    if rating is None:
        writer.submit(CLEAR_SQL, (photo_id,))
    else:
        writer.submit(RATE_SQL, (photo_id, rating.value, utc_now()))
    payload = _payload(photo_id, rating)
    writer.submit(LOG_SQL, (seq % RING, "rate", payload, utc_now()))
    writer.submit(PUT_SQL, ("action_seq", str(seq + 1)))
    writer.submit(PUT_SQL, ("undo_cursor", str(min(seq + 1, RING))))


def _payload(photo_id: int, rating: Rating | None) -> str:
    import json

    after: str | None = rating.value if rating else None
    data: dict[str, Any] = {"photo_id": photo_id, "after": after}
    return json.dumps(data)
