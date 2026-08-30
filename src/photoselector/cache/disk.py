"""On-disk LRU under .photoselector/{thumbs,previews}."""

from __future__ import annotations

from pathlib import Path

from photoselector.imaging.handle import ImageHandle

DEFAULT_BUDGET = 4 * 1024 * 1024 * 1024
_THUMB = {256, 512}


class DiskCache:
    """PNG files named by cache key. Tracks size so put() does not rglob."""

    def __init__(self, root: Path, budget: int = DEFAULT_BUDGET) -> None:
        self._root = root
        self._budget = budget
        (root / "thumbs").mkdir(parents=True, exist_ok=True)
        (root / "previews").mkdir(parents=True, exist_ok=True)
        self._sizes: dict[Path, int] = {}
        self._total = 0
        self._index()

    def get(self, key: str, size: int) -> ImageHandle | None:
        """Load a cached PNG, or None on miss."""
        path = self._path(key, size)
        if not path.is_file():
            return None
        data = path.read_bytes()
        path.touch()
        return _from_png(data)

    def put(self, key: str, size: int, handle: ImageHandle) -> None:
        """Write PNG bytes and evict if over budget."""
        path = self._path(key, size)
        path.write_bytes(handle.png_bytes)
        self._remember(path)
        self._evict()

    def _path(self, key: str, size: int) -> Path:
        folder = "thumbs" if size in _THUMB else "previews"
        return self._root / folder / f"{key}.png"

    def _index(self) -> None:
        for path in self._root.rglob("*.png"):
            if path.is_file():
                self._remember(path)

    def _remember(self, path: Path) -> None:
        try:
            nbytes = path.stat().st_size
        except OSError:
            return
        old = self._sizes.get(path)
        if old is not None:
            self._total -= old
        self._sizes[path] = nbytes
        self._total += nbytes

    def _evict(self) -> None:
        if self._total <= self._budget:
            return
        ranked = sorted(self._sizes, key=_atime)
        for path in ranked:
            if self._total <= self._budget:
                return
            nbytes = self._sizes.pop(path, 0)
            self._total -= nbytes
            path.unlink(missing_ok=True)


def _atime(path: Path) -> float:
    try:
        return path.stat().st_atime
    except OSError:
        return 0.0


def _from_png(data: bytes) -> ImageHandle:
    from io import BytesIO

    from PIL import Image

    image = Image.open(BytesIO(data))
    return ImageHandle.from_image(image)
