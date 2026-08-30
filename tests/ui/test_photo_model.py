from photoselector.catalog.models import Rating
from photoselector.catalog.queries import PhotoRecord
from photoselector.project.filter import FilterMode
from photoselector.project.store import PhotoList


def test_photo_list_rating_updates() -> None:
    record = PhotoRecord(1, "/a.jpg", "a.jpg", 1, 1, "jpeg", None, None, None, None, 0)
    store = PhotoList([record])
    store.set_rating(1, Rating.PICK)
    assert store.get(1).rating is Rating.PICK
    store.filter = FilterMode.PICKS
    assert len(store.visible()) == 1
    store.set_rating(1, None)
    assert store.visible() == []
