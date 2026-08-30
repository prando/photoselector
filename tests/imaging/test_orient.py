from pathlib import Path

from PIL import Image

from photoselector.imaging.decode import decode_path


def test_orientation_6_is_rotated(tmp_path: Path) -> None:
    path = tmp_path / "rot.jpg"
    image = Image.new("RGB", (10, 20), (200, 0, 0))
    exif = Image.Exif()
    exif[274] = 6
    image.save(path, exif=exif)
    handle = decode_path(path, 256)
    assert handle.width >= handle.height
