from pathlib import Path

from photoselector.imaging.keys import cache_key


def test_key_changes_with_mtime_and_size() -> None:
    path = Path("/tmp/a.jpg")
    a = cache_key(path, 1, 256)
    b = cache_key(path, 2, 256)
    c = cache_key(path, 1, 512)
    assert a != b
    assert a != c
    assert a == cache_key(path, 1, 256)
