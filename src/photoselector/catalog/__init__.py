"""SQLite catalog: schema, writer queue, and models."""

from photoselector.catalog.action_log import clamp_cursor, log_action, undo_cursor
from photoselector.catalog.connection import open_reader, open_writer
from photoselector.catalog.migrate import migrate
from photoselector.catalog.models import (
    Photo,
    Rating,
    clear_rating,
    set_rating,
    upsert_photo,
)
from photoselector.catalog.writer import Writer

__all__ = [
    "Photo",
    "Rating",
    "Writer",
    "clamp_cursor",
    "clear_rating",
    "log_action",
    "migrate",
    "open_reader",
    "open_writer",
    "set_rating",
    "undo_cursor",
    "upsert_photo",
]
