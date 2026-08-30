from tests.helpers import rec

from photoselector.project.filter import FilterMode, apply


def test_substring_filename() -> None:
    records = [rec(1, "DSC_1001.jpg"), rec(2, "IMG_9.png", fmt="png")]
    found = apply(records, FilterMode.ALL, "dsc")
    assert [row.filename for row in found] == ["DSC_1001.jpg"]
