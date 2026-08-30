"""Launch screen: open a folder, recents, and a drop target."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class WelcomePage(QWidget):
    """Shown when there is no last project, or after File → Close."""

    open_requested = Signal()
    path_chosen = Signal(object)

    def __init__(self, recents: list[Path]) -> None:
        super().__init__()
        self.setAcceptDrops(True)
        self._build(recents)

    def _build(self, recents: list[Path]) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)
        title = QLabel("PhotoSelector")
        title.setObjectName("title")
        hint = QLabel(
            "Open a folder of photos to start culling, or choose a recent project."
        )
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addLayout(self._buttons())
        layout.addWidget(self._drop_zone())
        layout.addWidget(self._recent_list(recents), 1)

    def _buttons(self) -> QHBoxLayout:
        row = QHBoxLayout()
        open_btn = QPushButton("Open folder")
        open_btn.setToolTip("Open folder")
        open_btn.clicked.connect(self.open_requested.emit)
        drive_btn = QPushButton("Open Google Drive folder")
        drive_btn.setObjectName("driveButton")
        drive_btn.setEnabled(False)
        drive_btn.setToolTip("Drive lands in M05")
        drive_btn.setCursor(Qt.CursorShape.ForbiddenCursor)
        row.addWidget(open_btn)
        row.addWidget(drive_btn)
        row.addStretch(1)
        return row

    def _drop_zone(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("dropZone")
        box = QVBoxLayout(frame)
        label = QLabel("Drop a folder here")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.addWidget(label)
        return frame

    def _recent_list(self, recents: list[Path]) -> QListWidget:
        listing = QListWidget()
        listing.setToolTip("Recent projects")
        if not recents:
            empty = QListWidgetItem("No recent projects")
            empty.setFlags(Qt.ItemFlag.NoItemFlags)
            listing.addItem(empty)
        for path in recents:
            item = QListWidgetItem(str(path))
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            listing.addItem(item)
        listing.itemActivated.connect(self._activate)
        return listing

    def _activate(self, item: QListWidgetItem) -> None:
        raw = item.data(Qt.ItemDataRole.UserRole)
        if raw:
            self.path_chosen.emit(Path(str(raw)))

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.is_dir():
                self.path_chosen.emit(path)
                return
