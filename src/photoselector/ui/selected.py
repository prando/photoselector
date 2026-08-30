"""Live picks list on the right dock."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from photoselector.catalog.queries import PhotoRecord
from photoselector.ui.shortcuts import tooltip


class SelectedPanel(QWidget):
    """Header 'Picks N'; click jumps; context menu remove / export-one."""

    jump_to = Signal(int)
    remove_requested = Signal(int)
    export_one = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._ids: list[int] = []
        self._header = QLabel("Picks 0")
        self._hint = QLabel("Press P to pick · X to reject")
        self._hint.setObjectName("hint")
        self._hint.setWordWrap(True)
        self._list = QListWidget()
        self._list.itemClicked.connect(self._click)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._menu)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self._header)
        layout.addWidget(self._hint)
        layout.addWidget(self._list, 1)
        self.set_picks([])

    def set_picks(self, picks: list[PhotoRecord]) -> None:
        """Replace the list and header count."""
        ids = [record.id for record in picks]
        self._header.setText(f"Picks {len(picks)}")
        self._hint.setVisible(not picks)
        if ids == self._ids and self._list.count() > 0:
            return
        self._ids = ids
        self._list.clear()
        for record in picks:
            item = QListWidgetItem(record.filename)
            item.setData(Qt.ItemDataRole.UserRole, record.id)
            self._list.addItem(item)

    def _click(self, item: QListWidgetItem) -> None:
        photo_id = item.data(Qt.ItemDataRole.UserRole)
        if photo_id is not None:
            self.jump_to.emit(int(photo_id))

    def _menu(self, pos: QPoint) -> None:
        item = self._list.itemAt(pos)
        if item is None:
            return
        photo_id = item.data(Qt.ItemDataRole.UserRole)
        if photo_id is None:
            return
        menu = QMenu(self)
        remove = QAction(tooltip("unrate", "Remove from selection"), self)
        remove.triggered.connect(lambda: self.remove_requested.emit(int(photo_id)))
        export = QAction("Export this photo only", self)
        export.triggered.connect(lambda: self.export_one.emit(int(photo_id)))
        menu.addAction(remove)
        menu.addAction(export)
        menu.exec(self._list.mapToGlobal(pos))
