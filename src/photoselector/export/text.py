"""Write absolute pick paths, taken_at then filename."""

from __future__ import annotations

from pathlib import Path

from photoselector.catalog.models import Rating
from photoselector.catalog.queries import PhotoRecord


def ordered_picks(records: list[PhotoRecord]) -> list[PhotoRecord]:
    """Picks only, EXIF taken-at then filename."""
    picks = [record for record in records if record.rating is Rating.PICK]
    return sorted(picks, key=lambda rec: (rec.taken_at or rec.filename, rec.filename))


def write_pick_list(path: Path, records: list[PhotoRecord]) -> int:
    """Write one absolute path per line. Returns pick count."""
    picks = ordered_picks(records)
    lines = [f"{record.path}\n" for record in picks]
    path.write_text("".join(lines), encoding="utf-8")
    return len(picks)
