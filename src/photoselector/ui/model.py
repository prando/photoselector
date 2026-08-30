"""QAbstractListModel over PhotoList."""

from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QPixmap

from photoselector.catalog.models import Rating
from photoselector.catalog.queries import PhotoRecord
from photoselector.project.store import PhotoList

_Index = QModelIndex | QPersistentModelIndex

IdRole = Qt.ItemDataRole.UserRole
RatingRole = Qt.ItemDataRole.UserRole + 1


class PhotoListModel(QAbstractListModel):
    """Virtualized list of the current filter."""

    def __init__(self, store: PhotoList) -> None:
        super().__init__()
        self._store = store
        self._pixmaps: dict[int, QPixmap] = {}

    def rowCount(self, parent: _Index | None = None) -> int:
        """Visible count."""
        del parent
        return len(self._store.visible())

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> object:
        """Filename, decoration, id, rating."""
        if not index.isValid():
            return None
        visible = self._store.visible()
        if index.row() >= len(visible):
            return None
        record = visible[index.row()]
        return self._role(record, role)

    def _role(self, record: PhotoRecord, role: int) -> object:
        if role == Qt.ItemDataRole.DisplayRole:
            return record.filename
        if role == Qt.ItemDataRole.DecorationRole:
            return self._pixmaps.get(record.id)
        if role == Qt.ItemDataRole.ToolTipRole:
            return record.filename
        if role == int(IdRole):
            return record.id
        if role == int(RatingRole):
            return record.rating.value if record.rating else ""
        return None

    def set_pixmap(self, photo_id: int, pixmap: QPixmap) -> None:
        """Attach a thumbnail and refresh that row only."""
        if not self._should_store(photo_id, pixmap):
            return
        self._pixmaps[photo_id] = pixmap
        self._emit_row(photo_id, [Qt.ItemDataRole.DecorationRole])

    def pixmap(self, photo_id: int) -> QPixmap | None:
        """Cached decoration for this photo, if decoded."""
        return self._pixmaps.get(photo_id)

    def notify_rating(self, photo_id: int) -> None:
        """Badge/opacity changed; filter membership did not."""
        self._emit_row(
            photo_id, [int(RatingRole), Qt.ItemDataRole.DecorationRole]
        )

    def reset_view(self) -> None:
        """Filter or ratings changed membership."""
        self.beginResetModel()
        self.endResetModel()

    def record_at(self, row: int) -> PhotoRecord | None:
        """Visible record or None."""
        visible = self._store.visible()
        if 0 <= row < len(visible):
            return visible[row]
        return None

    def badge(self, row: int) -> str:
        """P / X / empty for the delegate."""
        record = self.record_at(row)
        if record is None or record.rating is None:
            return ""
        return "P" if record.rating is Rating.PICK else "X"

    def _should_store(self, photo_id: int, pixmap: QPixmap) -> bool:
        old = self._pixmaps.get(photo_id)
        if old is None or old.isNull() or pixmap.isNull():
            return True
        old_area = old.width() * old.height()
        new_area = pixmap.width() * pixmap.height()
        return new_area > old_area

    def _emit_row(self, photo_id: int, roles: list[int]) -> None:
        row = self._row_of(photo_id)
        if row is None:
            return
        idx = self.index(row)
        self.dataChanged.emit(idx, idx, roles)

    def _row_of(self, photo_id: int) -> int | None:
        for row, record in enumerate(self._store.visible()):
            if record.id == photo_id:
                return row
        return None
