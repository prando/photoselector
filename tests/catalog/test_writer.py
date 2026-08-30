from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import pytest

from photoselector.catalog.connection import open_reader, open_writer
from photoselector.catalog.migrate import migrate
from photoselector.catalog.writer import Writer


def _insert_kv(key: str, value: str) -> tuple[str, tuple[str, str]]:
    return (
        "INSERT OR REPLACE INTO project_data(key, value) VALUES (?, ?)",
        (key, value),
    )


def test_hundred_writes_flush_as_one_batch(tmp_path: Path) -> None:
    commits: list[int] = []
    db = tmp_path / "catalog.db"
    writer = Writer(db, on_commit=commits.append)
    for index in range(100):
        sql, params = _insert_kv(f"k{index}", str(index))
        writer.submit(sql, params)
    writer.flush()
    writer.close()
    assert commits == [100]
    reader = open_reader(db)
    count = reader.execute("SELECT COUNT(*) FROM project_data").fetchone()
    assert int(count[0]) >= 100
    reader.close()


def test_idle_flush_after_interval(tmp_path: Path) -> None:
    commits: list[int] = []
    db = tmp_path / "catalog.db"
    writer = Writer(db, interval=0.05, on_commit=commits.append)
    sql, params = _insert_kv("idle", "1")
    writer.submit(sql, params)
    time.sleep(0.2)
    assert commits == [1]
    writer.close()


def test_reader_cannot_write(tmp_path: Path) -> None:
    db = tmp_path / "catalog.db"
    conn = open_writer(db)
    migrate(conn)
    conn.close()
    reader = open_reader(db)
    with pytest.raises(sqlite3.OperationalError):
        reader.execute("INSERT INTO project_data(key, value) VALUES ('x', 'y')")
    reader.close()
