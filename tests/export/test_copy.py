from pathlib import Path

from tests.helpers import rec

from photoselector.catalog.models import Rating
from photoselector.export.copy import copy_picks


def test_copy_and_rename(tmp_path: Path) -> None:
    src = tmp_path / "orig.jpg"
    src.write_bytes(b"jpeg")
    record = rec(1, "orig.jpg", rating=Rating.PICK, path=str(src))
    dest = tmp_path / "out"
    assert copy_picks([record], dest, rename=True) == 1
    assert (dest / "0001_orig.jpg").is_file()
    cancelled = copy_picks([record], dest, cancel=lambda: True)
    assert cancelled == 0
