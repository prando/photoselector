"""Inline error / version banner. Not a modal."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel


class Banner(QLabel):
    """Slim top-of-window message."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("banner")
        self.setVisible(False)
        self.setWordWrap(True)

    def show_message(self, text: str) -> None:
        """Show an inline message."""
        self.setText(text)
        self.setVisible(True)

    def clear(self) -> None:
        """Hide the banner."""
        self.setText("")
        self.setVisible(False)
