from PIL import Image, ImageDraw

from photoselector.imaging.phash import average_hash, same_group


def test_identical_group_and_opposite() -> None:
    white = Image.new("RGB", (32, 32), "white")
    same = Image.new("RGB", (32, 32), "white")
    assert same_group(average_hash(white), average_hash(same))
    striped = Image.new("RGB", (32, 32), "white")
    ImageDraw.Draw(striped).rectangle((0, 0, 16, 32), fill="black")
    assert not same_group(average_hash(white), average_hash(striped))
