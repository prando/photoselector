from __future__ import annotations

from pathlib import Path

from photoselector.catalog.action_log import RING, clamp_cursor, log_action, undo_cursor
from photoselector.catalog.connection import open_writer
from photoselector.catalog.migrate import migrate


def test_ring_keeps_500_rows(tmp_path: Path) -> None:
    conn = open_writer(tmp_path / "catalog.db")
    migrate(conn)
    for index in range(RING + 1):
        log_action(conn, "rate", {"i": index})
    count = conn.execute("SELECT COUNT(*) FROM action_log").fetchone()
    assert int(count[0]) == RING
    conn.close()


def test_undo_cursor_clamps(tmp_path: Path) -> None:
    conn = open_writer(tmp_path / "catalog.db")
    migrate(conn)
    log_action(conn, "rate", {"i": 0})
    conn.execute(
        "INSERT OR REPLACE INTO project_data(key, value) VALUES ('undo_cursor', '999')"
    )
    assert clamp_cursor(conn) == 1
    assert undo_cursor(conn) == 1
    conn.close()
