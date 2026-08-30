"""Open a local folder as a PhotoSelector project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from photoselector.catalog.models import UPSERT_SQL, Photo, utc_now
from photoselector.catalog.writer import Writer
from photoselector.project.hygiene import catalog_path, prepare_project
from photoselector.project.scan import iter_photos


@dataclass(frozen=True)
class Session:
    """An opened project and the number of photos ingested."""

    root: Path
    photo_count: int
    db_path: Path


def open_session(root: Path) -> Session:
    """Prepare cache, migrate the catalog, and ingest photos."""
    prepare_project(root)
    db_path = catalog_path(root)
    writer = Writer(db_path)
    try:
        count = _ingest(root, writer)
    finally:
        writer.close()
    return Session(root=root, photo_count=count, db_path=db_path)


def _ingest(root: Path, writer: Writer) -> int:
    photos = iter_photos(root)
    for photo in photos:
        writer.submit(UPSERT_SQL, _params(photo))
    writer.flush()
    return len(photos)


def _params(photo: Photo) -> tuple[object, ...]:
    return (
        photo.path,
        photo.filename,
        photo.mtime_ns,
        photo.size_bytes,
        photo.taken_at,
        photo.orientation,
        photo.fmt,
        utc_now(),
    )
