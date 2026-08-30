"""Load the dark or light Qt stylesheet."""

from __future__ import annotations

from importlib import resources

from PySide6.QtWidgets import QApplication

ThemeName = str


def apply_theme(app: QApplication, name: ThemeName = "dark") -> None:
    """Apply `ui/themes/{name}.qss`. Unknown names fall back to dark."""
    filename = "light.qss" if name == "light" else "dark.qss"
    root = resources.files("photoselector.ui.themes")
    app.setStyleSheet(root.joinpath(filename).read_text(encoding="utf-8"))
