"""shutil.copy2 of picks into a target folder."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from photoselector.catalog.queries import PhotoRecord
from photoselector.export.text import ordered_picks


def copy_picks(
    records: list[PhotoRecord],
    target: Path,
    *,
    rename: bool = False,
    cancel: Callable[[], bool] | None = None,
) -> int:
    """Copy picks. `rename` uses {index:04d}_{original}."""
    target.mkdir(parents=True, exist_ok=True)
    copied = 0
    for index, record in enumerate(ordered_picks(records), start=1):
        if cancel is not None and cancel():
            break
        name = _name(record, index, rename)
        shutil.copy2(record.path, target / name)
        copied += 1
    return copied


def _name(record: PhotoRecord, index: int, rename: bool) -> str:
    if not rename:
        return record.filename
    return f"{index:04d}_{record.filename}"
