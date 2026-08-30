"""Discover supported photos in a project folder."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from photoselector.catalog.models import Format, Photo
from photoselector.project.hygiene import CACHE_DIR

EXTENSIONS: dict[str, Format] = {
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".png": "png",
    ".heic": "heic",
    ".heif": "heic",
    ".cr2": "raw",
    ".cr3": "raw",
    ".nef": "raw",
    ".arw": "raw",
    ".dng": "raw",
    ".raf": "raw",
    ".orf": "raw",
}


def iter_photos(root: Path) -> list[Photo]:
    """Scan the project root and one level of subfolders."""
    found: list[Photo] = []
    found.extend(_collect(root))
    for child in _child_dirs(root):
        found.extend(_collect(child))
    return found


def _child_dirs(root: Path) -> Iterator[Path]:
    try:
        entries = sorted(root.iterdir())
    except OSError:
        return
    for child in entries:
        if child.is_dir() and child.name != CACHE_DIR:
            yield child


def _collect(folder: Path) -> list[Photo]:
    photos: list[Photo] = []
    try:
        entries = sorted(folder.iterdir())
    except OSError:
        return photos
    for path in entries:
        photo = _from_file(path)
        if photo is not None:
            photos.append(photo)
    return photos


def _from_file(path: Path) -> Photo | None:
    if not path.is_file():
        return None
    fmt = EXTENSIONS.get(path.suffix.lower())
    if fmt is None:
        return None
    stat = path.stat()
    return Photo(
        path=str(path.resolve()),
        filename=path.name,
        mtime_ns=stat.st_mtime_ns,
        size_bytes=stat.st_size,
        fmt=fmt,
    )
