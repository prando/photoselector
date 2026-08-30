from photoselector.cache.ram import RamCache
from photoselector.imaging.handle import ImageHandle


def test_ram_evicts_oldest() -> None:
    cache = RamCache(budget=20)
    cache.put("a", ImageHandle(1, 1, b"1234567890"))
    cache.put("b", ImageHandle(1, 1, b"1234567890"))
    cache.put("c", ImageHandle(1, 1, b"1234567890"))
    assert cache.get("a") is None
    assert cache.get("c") is not None
