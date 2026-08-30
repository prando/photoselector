from tests.helpers import rec

from photoselector.catalog.models import Rating
from photoselector.project.filter import FilterMode, apply


def test_filter_counts() -> None:
    records = [
        rec(1, "a.jpg", rating=Rating.PICK),
        rec(2, "b.jpg", rating=Rating.REJECT),
        rec(3, "c.jpg"),
    ]
    assert len(apply(records, FilterMode.ALL)) == 3
    assert len(apply(records, FilterMode.PICKS)) == 1
    assert len(apply(records, FilterMode.REJECTS)) == 1
    assert len(apply(records, FilterMode.UNRATED)) == 1
    assert apply(records, FilterMode.ALL, "b.")[0].filename == "b.jpg"
