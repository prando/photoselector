"""Bottom filmstrip bound to the same filter model."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QListView

from photoselector.ui.grid import ThumbnailDelegate, nudge_view
from photoselector.ui.model import PhotoListModel


class FilmstripView(QListView):
    """Horizontal icon strip."""

    def __init__(self, model: PhotoListModel) -> None:
        super().__init__()
        self.setModel(model)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setMovement(QListView.Movement.Static)
        icon = QSize(96, 96)
        cell = QSize(110, 110)
        self.setIconSize(icon)
        self.setGridSize(cell)
        self.setItemDelegate(ThumbnailDelegate(icon, cell, self, badges=True))
        self.setMaximumHeight(130)
        self.setWrapping(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyboardSearch(self, search: str) -> None:
        """Skip type-ahead so P/X/U reach cull shortcuts."""
        del search

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Left/Right step one photo along the strip."""
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
