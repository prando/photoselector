from pathlib import Path

from tests.helpers import rec

from photoselector.catalog.models import Rating
from photoselector.export.text import ordered_picks, write_pick_list


def test_text_list_order(tmp_path: Path) -> None:
    records = [
        rec(1, "b.jpg", rating=Rating.PICK, taken="2020-02-01"),
        rec(2, "a.jpg", rating=Rating.PICK, taken="2020-01-01"),
        rec(3, "c.jpg", rating=Rating.REJECT),
        rec(4, "d.jpg"),
    ]
    picks = ordered_picks(records)
    assert [row.filename for row in picks] == ["a.jpg", "b.jpg"]
    dest = tmp_path / "picks.txt"
    assert write_pick_list(dest, records) == 2
    assert dest.read_text(encoding="utf-8").splitlines() == ["/a.jpg", "/b.jpg"]
