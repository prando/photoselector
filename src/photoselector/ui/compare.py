"""2–4 synced loupe tiles. Keys 1–4 pick that tile."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGridLayout, QWidget

from photoselector.catalog.queries import PhotoRecord
from photoselector.ui.loupe import LoupeView


class CompareView(QWidget):
    """Requires 2–4 records. `on_pick(index)` when 1–4 is pressed."""

    def __init__(self, on_pick: Callable[[int], None]) -> None:
        super().__init__()
        self._on_pick = on_pick
        self._tiles: list[LoupeView] = []
        self._records: list[PhotoRecord] = []
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)

    def set_records(self, records: list[PhotoRecord]) -> None:
        """Rebuild 2–4 tiles."""
        self._clear()
        self._records = records[:4]
        positions = ((0, 0), (0, 1), (1, 0), (1, 1))
        for index, record in enumerate(self._records):
            tile = LoupeView()
            tile.setToolTip(record.filename)
            self._tiles.append(tile)
            row, col = positions[index]
            self._layout.addWidget(tile, row, col)

    def set_pixmap(self, index: int, pixmap: QPixmap) -> None:
        """Fill one tile."""
        if 0 <= index < len(self._tiles):
            self._tiles[index].set_pixmap(pixmap)

    def pick(self, slot: int) -> PhotoRecord | None:
        """1-based slot. Returns the chosen record."""
        index = slot - 1
        if index < 0 or index >= len(self._records):
            return None
        self._on_pick(index)
        return self._records[index]

    def records(self) -> list[PhotoRecord]:
        """Current compare set."""
        return list(self._records)

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                break
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._tiles.clear()
        self._records.clear()


def allowed(count: int) -> bool:
    """Compare requires 2–4 selected photos."""
    return 2 <= count <= 4
