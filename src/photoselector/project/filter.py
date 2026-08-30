"""Visible-set filters over a photo list."""

from __future__ import annotations

from enum import Enum

from photoselector.catalog.models import Rating
from photoselector.catalog.queries import PhotoRecord


class FilterMode(Enum):
    """Ctrl+1..4 filter chips."""

    ALL = "all"
    PICKS = "picks"
    REJECTS = "rejects"
    UNRATED = "unrated"


def matches(record: PhotoRecord, mode: FilterMode, search: str) -> bool:
    """True if the record belongs in the current filter + filename search."""
    if not _rating_ok(record.rating, mode):
        return False
    needle = search.strip().lower()
    if needle and needle not in record.filename.lower():
        return False
    return True


def apply(
    records: list[PhotoRecord], mode: FilterMode, search: str = ""
) -> list[PhotoRecord]:
    """Filter a list."""
    return [record for record in records if matches(record, mode, search)]


def _rating_ok(rating: Rating | None, mode: FilterMode) -> bool:
    if mode is FilterMode.ALL:
        return True
    if mode is FilterMode.PICKS:
        return rating is Rating.PICK
    if mode is FilterMode.REJECTS:
        return rating is Rating.REJECT
    return rating is None
