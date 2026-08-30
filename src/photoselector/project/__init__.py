"""Project folder scan, hygiene, recents, and session open."""

from photoselector.project.hygiene import catalog_path, prepare_project
from photoselector.project.recent import RecentStore
from photoselector.project.scan import EXTENSIONS, iter_photos
from photoselector.project.session import Session, open_session

__all__ = [
    "EXTENSIONS",
    "RecentStore",
    "Session",
    "catalog_path",
    "iter_photos",
    "open_session",
    "prepare_project",
]
