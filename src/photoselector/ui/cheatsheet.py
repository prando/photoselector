"""Searchable non-modal keyboard cheatsheet."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLineEdit, QListWidget, QVBoxLayout

from photoselector.ui.shortcuts import DEFAULTS


class Cheatsheet(QDialog):
    """Help → Keyboard shortcuts."""

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)  # type: ignore[arg-type]
        self.setWindowTitle("Keyboard shortcuts")
        self.setModal(False)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search")
        self._search.textChanged.connect(self._filter)
        self._list = QListWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self._search)
        layout.addWidget(self._list)
        self._rows = [f"{name}: {key}" for name, key in sorted(DEFAULTS.items())]
        self._filter("")

    def _filter(self, text: str) -> None:
        needle = text.lower()
        self._list.clear()
        for row in self._rows:
            if needle in row.lower():
                self._list.addItem(row)
