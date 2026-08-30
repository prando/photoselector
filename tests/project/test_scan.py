from __future__ import annotations

from pathlib import Path

from photoselector.catalog.connection import open_reader
from photoselector.catalog.models import photo_count
from photoselector.project.hygiene import CACHE_DIR
from photoselector.project.scan import iter_photos
from photoselector.project.session import open_session


def test_scan_collects_supported_and_skips_others(tmp_path: Path) -> None:
    (tmp_path / "keep.jpg").write_bytes(b"j")
    (tmp_path / "keep.CR2").write_bytes(b"r")
    (tmp_path / "notes.txt").write_bytes(b"x")
    nested = tmp_path / "day1"
    nested.mkdir()
    (nested / "nested.png").write_bytes(b"p")
    cache = tmp_path / CACHE_DIR
    cache.mkdir()
    (cache / "ignored.jpg").write_bytes(b"no")
    photos = iter_photos(tmp_path)
    names = {photo.filename for photo in photos}
    assert names == {"keep.jpg", "keep.CR2", "nested.png"}


def test_open_session_ingests_jpeg(tmp_path: Path) -> None:
    (tmp_path / "a.jpg").write_bytes(b"jpeg")
    session = open_session(tmp_path)
    assert session.photo_count == 1
    reader = open_reader(session.db_path)
    assert photo_count(reader) == 1
    reader.close()
