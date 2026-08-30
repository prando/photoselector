from pathlib import Path

from PIL import Image

from photoselector.cache.disk import DiskCache
from photoselector.imaging.handle import ImageHandle


def test_disk_roundtrip_and_evict(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path, budget=800)
    handle = ImageHandle.from_image(Image.new("RGB", (8, 8), "red"))
    cache.put("aaa", 256, handle)
    loaded = cache.get("aaa", 256)
    assert loaded is not None
    assert loaded.width == 8
    cache.put("bbb", 256, ImageHandle.from_image(Image.new("RGB", (8, 8), "blue")))
    assert cache.get("bbb", 256) is not None
