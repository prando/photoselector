"""Virtualized icon grid with pick/reject badges."""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
    QListView,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)

from photoselector.ui.model import PhotoListModel, RatingRole

_Index = QModelIndex | QPersistentModelIndex

ICON_SIZE = QSize(192, 192)
CELL_SIZE = QSize(210, 230)


class ThumbnailDelegate(QStyledItemDelegate):
    """Paint scaled thumbs. App QSS otherwise collapses IconMode decorations."""

    def __init__(
        self,
        icon: QSize,
        cell: QSize,
        parent: QListView | None = None,
        *,
        badges: bool = False,
    ) -> None:
        super().__init__(parent)
        self._icon = icon
        self._cell = cell
        self._badges = badges

    def sizeHint(self, option: QStyleOptionViewItem, index: _Index) -> QSize:
        """Keep cells at grid size even when stylesheets are active."""
        del option, index
        return self._cell

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: _Index,
    ) -> None:
        rating = str(index.data(int(RatingRole)) or "")
        painter.save()
        if rating == "reject":
            painter.setOpacity(0.4)
        self._draw_cell(painter, option, index)
        painter.restore()
        if self._badges and rating in {"pick", "reject"}:
            self._badge(painter, option, "P" if rating == "pick" else "X")

    def _draw_cell(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: _Index,
    ) -> None:
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor("#3d3d3d"))
        raw = index.data(Qt.ItemDataRole.DecorationRole)
        pixmap = raw if isinstance(raw, QPixmap) else None
        self._thumb(painter, option.rect, pixmap)
        name = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        self._label(painter, option.rect, name)

    def _thumb(self, painter: QPainter, cell: QRect, pixmap: QPixmap | None) -> None:
        box = QRect(
            cell.x() + (cell.width() - self._icon.width()) // 2,
            cell.y() + 6,
            self._icon.width(),
            self._icon.height(),
        )
        if pixmap is None or pixmap.isNull():
            painter.fillRect(box, QColor("#262626"))
            return
        scaled = pixmap.scaled(
            self._icon,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = box.x() + (box.width() - scaled.width()) // 2
        y = box.y() + (box.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)

    def _label(self, painter: QPainter, cell: QRect, name: str) -> None:
        text = QRect(
            cell.x() + 4,
            cell.y() + self._icon.height() + 8,
            cell.width() - 8,
            max(12, cell.height() - self._icon.height() - 12),
        )
        painter.setPen(QColor("#f4f4f4"))
        elided = painter.fontMetrics().elidedText(
            name, Qt.TextElideMode.ElideMiddle, max(8, text.width())
        )
        painter.drawText(
            text, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, elided
        )

    def _badge(
        self, painter: QPainter, option: QStyleOptionViewItem, text: str
    ) -> None:
        painter.save()
        color = QColor("#24a148") if text == "P" else QColor("#da1e28")
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        rect = option.rect.adjusted(6, 6, 0, 0)
        painter.drawRoundedRect(rect.left(), rect.top(), 18, 18, 4, 4)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(
            rect.left(), rect.top(), 18, 18, Qt.AlignmentFlag.AlignCenter, text
        )
        painter.restore()


class GridView(QListView):
    """IconMode grid, Shift/Cmd multi-select."""

    def __init__(self, model: PhotoListModel) -> None:
        super().__init__()
        self.setModel(model)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setWrapping(True)
        self.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.setIconSize(ICON_SIZE)
        self.setGridSize(CELL_SIZE)
        self.setUniformItemSizes(True)
        self.setWordWrap(True)
        self.setItemDelegate(
            ThumbnailDelegate(ICON_SIZE, CELL_SIZE, self, badges=True)
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyboardSearch(self, search: str) -> None:
        """Skip type-ahead so P/X/U reach cull shortcuts."""
        del search

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Left/Right step one photo. IconMode otherwise swallows them."""
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            super().keyPressEvent(event)
            return
        if event.key() == Qt.Key.Key_Right:
            nudge_view(self, 1)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Left:
            nudge_view(self, -1)
            event.accept()
            return
        super().keyPressEvent(event)


def nudge_view(view: QListView, delta: int) -> None:
    """Move the current row by `delta` and scroll it into view."""
    model = view.model()
    if model is None:
        return
    count = model.rowCount()
    if count <= 0:
        return
    current = view.currentIndex()
    row = current.row() if current.isValid() else 0
    row = min(max(0, row + delta), count - 1)
    idx = model.index(row, 0)
    view.setCurrentIndex(idx)
    view.scrollTo(idx)
