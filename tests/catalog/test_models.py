from __future__ import annotations

from pathlib import Path

from photoselector.catalog.connection import open_writer
from photoselector.catalog.migrate import migrate
from photoselector.catalog.models import (
    Photo,
    Rating,
    clear_rating,
    set_rating,
    upsert_photo,
)


def _photo(tmp_path: Path) -> Photo:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"jpeg")
    return Photo(
        path=str(path),
        filename="a.jpg",
        mtime_ns=1,
        size_bytes=4,
        fmt="jpeg",
    )


def test_pick_reject_unrate_leaves_no_selection_row(tmp_path: Path) -> None:
    conn = open_writer(tmp_path / "catalog.db")
    migrate(conn)
    photo_id = upsert_photo(conn, _photo(tmp_path))
    set_rating(conn, photo_id, Rating.PICK)
    set_rating(conn, photo_id, Rating.REJECT)
    clear_rating(conn, photo_id)
    row = conn.execute(
        "SELECT COUNT(*) FROM selection WHERE photo_id = ?", (photo_id,)
    ).fetchone()
    assert int(row[0]) == 0
    conn.close()
