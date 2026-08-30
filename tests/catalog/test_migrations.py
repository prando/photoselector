from __future__ import annotations

from pathlib import Path

from photoselector.catalog.connection import open_writer
from photoselector.catalog.migrate import migrate, schema_version


def test_migrate_is_idempotent(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    conn = open_writer(db)
    migrate(conn)
    migrate(conn)
    assert schema_version(conn) == 1
    conn.close()

    again = open_writer(db)
    migrate(again)
    assert schema_version(again) == 1
    again.close()
