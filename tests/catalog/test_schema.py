from __future__ import annotations

from pathlib import Path

from photoselector.catalog.connection import open_writer
from photoselector.catalog.migrate import migrate, schema_version

TABLES = {"photo", "selection", "action_log", "project_data", "drive_auth"}


def test_fresh_db_has_schema_version_and_tables(tmp_path: Path) -> None:
    conn = open_writer(tmp_path / "catalog.db")
    migrate(conn)
    assert schema_version(conn) == 1
    names = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert TABLES <= names
    conn.close()
