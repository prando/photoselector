from __future__ import annotations

from pathlib import Path

from photoselector.project.hygiene import CACHE_DIR, prepare_project


def test_prepare_project_writes_markers(tmp_path: Path) -> None:
    cache = prepare_project(tmp_path)
    assert cache == tmp_path / CACHE_DIR
    assert cache.is_dir()
    gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert CACHE_DIR in gitignore
    assert (cache / "CACHEDIR.TAG").is_file()
