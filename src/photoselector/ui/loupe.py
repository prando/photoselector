"""QGraphicsView loupe: wheel zoom, pan, fit, 1:1."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QPainter, QPixmap, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from photoselector.ui.zoom import ZoomMode, is_one_to_one


class LoupeView(QGraphicsView):
    """Single-photo viewer."""

    nudge = Signal(int)

    def __init__(self, *, arrows_nudge: bool = False) -> None:
        super().__init__()
        self._arrows_nudge = arrows_nudge
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._item = QGraphicsPixmapItem()
        self._scene.addItem(self._item)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._mode = ZoomMode.FIT
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    @property
    def mode(self) -> ZoomMode:
        """Current zoom mode."""
        return self._mode

    def set_pixmap(self, pixmap: QPixmap) -> None:
        """Replace the image and restore the current mode."""
        self._item.setPixmap(pixmap)
        self._scene.setSceneRect(pixmap.rect())
        self.apply_mode(self._mode)

    def apply_mode(self, mode: ZoomMode) -> None:
        """Fit or jump to 1:1."""
        self._mode = mode
        if is_one_to_one(mode):
            self.resetTransform()
            return
        self.fitInView(self._item, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom at cursor."""
        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else 1 / 1.15
        self.scale(factor, factor)
        event.accept()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Arrows change photos in the main loupe; compare tiles ignore them."""
        delta = _arrow_delta(event.key())
        if delta is None:
            super().keyPressEvent(event)
            return
        if self._arrows_nudge and delta != 0:
            self.nudge.emit(delta)
            event.accept()
            return
        event.ignore()


def _arrow_delta(key: int) -> int | None:
    if key == Qt.Key.Key_Right:
        return 1
    if key == Qt.Key.Key_Left:
        return -1
    if key in {Qt.Key.Key_Up, Qt.Key.Key_Down}:
        return 0
    return None
