"""Cull + undo that update memory immediately and queue SQLite."""

from __future__ import annotations

from dataclasses import dataclass

from photoselector.catalog.cull import enqueue_rating
from photoselector.catalog.models import Rating
from photoselector.catalog.writer import Writer
from photoselector.project.store import PhotoList


@dataclass
class _Step:
    photo_id: int
    before: Rating | None
    after: Rating | None


class CullController:
    """P/X/U plus undo/redo. Memory first, writer second."""

    def __init__(self, store: PhotoList, writer: Writer) -> None:
        self._store = store
        self._writer = writer
        self._undo: list[_Step] = []
        self._redo: list[_Step] = []
        self._seq = 0

    def rate(self, photo_id: int, rating: Rating | None) -> None:
        """Apply a cull mutation."""
        before = self._store.set_rating(photo_id, rating)
        if before == rating:
            return
        step = _Step(photo_id, before, rating)
        self._undo.append(step)
        self._redo.clear()
        enqueue_rating(self._writer, photo_id, rating, seq=self._seq)
        self._seq += 1

    def undo(self) -> bool:
        """Restore the previous rating. False if the stack is empty."""
        if not self._undo:
            return False
        step = self._undo.pop()
        self._store.set_rating(step.photo_id, step.before)
        self._redo.append(step)
        enqueue_rating(self._writer, step.photo_id, step.before, seq=self._seq)
        self._seq += 1
        return True

    def redo(self) -> bool:
        """Re-apply an undone rating."""
        if not self._redo:
            return False
        step = self._redo.pop()
        self._store.set_rating(step.photo_id, step.after)
        self._undo.append(step)
        enqueue_rating(self._writer, step.photo_id, step.after, seq=self._seq)
        self._seq += 1
        return True
