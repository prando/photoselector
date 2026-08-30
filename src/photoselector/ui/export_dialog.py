"""Export confirmation (allowed modal)."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from photoselector.catalog.queries import PhotoRecord
from photoselector.export.copy import copy_picks
from photoselector.export.text import write_pick_list


def export_text(parent: QWidget, records: list[PhotoRecord]) -> Path | None:
    """Ask for a .txt path and write picks."""
    path, _ok = QFileDialog.getSaveFileName(
        parent, "Export pick list", "selected_photos.txt", "Text (*.txt)"
    )
    if not path:
        return None
    dest = Path(path)
    write_pick_list(dest, records)
    return dest


def export_copy(parent: QWidget, records: list[PhotoRecord]) -> Path | None:
    """Ask for a folder and copy2 picks."""
    dest = QFileDialog.getExistingDirectory(parent, "Copy picks to folder")
    if not dest:
        return None
    target = Path(dest)
    try:
        copy_picks(records, target)
    except OSError as exc:
        QMessageBox.critical(parent, "Export failed", str(exc))
        return None
    return target


def export_one(parent: QWidget, record: PhotoRecord) -> Path | None:
    """Copy a single photo."""
    return export_copy(parent, [record])
