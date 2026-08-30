"""Convert ImageHandle to QPixmap on the GUI thread."""

from __future__ import annotations

from PySide6.QtGui import QImage, QPixmap

from photoselector.imaging.handle import ImageHandle


def to_pixmap(handle: ImageHandle) -> QPixmap:
    """Blit pixels. Call only on the UI thread."""
    return QPixmap.fromImage(to_qimage(handle))


def to_qimage(handle: ImageHandle) -> QImage:
    """Copy raw pixels into a QImage without QImage.fromData."""
    return _blit(handle)


def _blit(handle: ImageHandle) -> QImage:
    """Copy RGB/RGBA bytes into a detached QImage."""
    fmt = (
        QImage.Format.Format_RGBA8888
        if handle.channels == 4
        else QImage.Format.Format_RGB888
    )
    width, height = handle.width, handle.height
    qimage = QImage(width, height, fmt)
    payload = handle.pixels
    src_stride = width * handle.channels
    dest_stride = qimage.bytesPerLine()
    dest = memoryview(qimage.bits()).cast("B")
    if dest_stride == src_stride:
        dest[: len(payload)] = payload
    else:
        for y in range(height):
            d0 = y * dest_stride
            s0 = y * src_stride
            dest[d0 : d0 + src_stride] = payload[s0 : s0 + src_stride]
    return qimage
