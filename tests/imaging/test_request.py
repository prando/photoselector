from pathlib import Path

from PIL import Image

from photoselector.imaging.service import ImagingService, Priority


def test_request_then_ram_hit(tmp_path: Path) -> None:
    photo = tmp_path / "a.jpg"
    Image.new("RGB", (32, 32), (10, 20, 30)).save(photo)
    service = ImagingService(tmp_path / "cache", workers=1)
    first = service.request(photo, 64, Priority.P0, photo.stat().st_mtime_ns)
    handle = first.result(timeout=5)
    assert handle.width > 0
    second = service.request(photo, 64, Priority.P0, photo.stat().st_mtime_ns)
    assert second.result(timeout=1).pixels == handle.pixels
    assert service.ram_get(photo, 64, photo.stat().st_mtime_ns) is not None
    service.close()
