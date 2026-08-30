from pathlib import Path

from photoselector.catalog.connection import open_reader, open_writer
from photoselector.catalog.migrate import migrate
from photoselector.catalog.models import Photo, Rating, upsert_photo
from photoselector.catalog.queries import load_photos
from photoselector.catalog.writer import Writer
from photoselector.project.controller import CullController
from photoselector.project.store import PhotoList


def test_undo_pick_restores_unrated(tmp_path: Path) -> None:
    db = tmp_path / "c.db"
    conn = open_writer(db)
    migrate(conn)
    photo_id = upsert_photo(conn, Photo(str(tmp_path / "a.jpg"), "a.jpg", 1, 1, "jpeg"))
    conn.close()
    writer = Writer(db)
    store = PhotoList(load_photos(open_reader(db)))
    ctl = CullController(store, writer)
    ctl.rate(photo_id, Rating.PICK)
    assert store.get(photo_id).rating is Rating.PICK
    assert ctl.undo()
    assert store.get(photo_id).rating is None
    assert ctl.redo()
    assert store.get(photo_id).rating is Rating.PICK
    writer.close()
