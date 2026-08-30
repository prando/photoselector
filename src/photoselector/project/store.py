"""In-memory photo list with instant cull updates."""

from __future__ import annotations

from photoselector.catalog.models import Rating
from photoselector.catalog.queries import PhotoRecord
from photoselector.project.filter import FilterMode, apply


class PhotoList:
    """Mutable façade used by the Qt model and by tests."""

    def __init__(self, photos: list[PhotoRecord]) -> None:
        self._photos = {record.id: record for record in photos}
        self._order = [record.id for record in photos]
        self.filter = FilterMode.ALL
        self.search = ""

    def visible(self) -> list[PhotoRecord]:
        """Photos in the current filter, catalog order."""
        records = [self._photos[photo_id] for photo_id in self._order]
        return apply(records, self.filter, self.search)

    def picks(self) -> list[PhotoRecord]:
        """Picked photos in catalog order."""
        return [
            self._photos[photo_id]
            for photo_id in self._order
            if self._photos[photo_id].rating is Rating.PICK
        ]

    def all_records(self) -> list[PhotoRecord]:
        """Every photo, ignoring the current filter."""
        return [self._photos[photo_id] for photo_id in self._order]

    def get(self, photo_id: int) -> PhotoRecord:
        """Lookup by id."""
        return self._photos[photo_id]

    def set_rating(self, photo_id: int, rating: Rating | None) -> Rating | None:
        """Replace rating; return previous. Does not touch SQLite."""
        current = self._photos[photo_id]
        previous = current.rating
        self._photos[photo_id] = PhotoRecord(
            id=current.id,
            path=current.path,
            filename=current.filename,
            mtime_ns=current.mtime_ns,
            size_bytes=current.size_bytes,
            fmt=current.fmt,
            taken_at=current.taken_at,
            rating=rating,
            stars=current.stars,
            color=current.color,
            rotate_quarters=current.rotate_quarters,
        )
        return previous

    def __len__(self) -> int:
        return len(self._order)
