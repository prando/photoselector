"""In-memory LRU of ImageHandle, budgeted in raw pixel bytes."""

from __future__ import annotations

from collections import OrderedDict

from photoselector.imaging.handle import ImageHandle

DEFAULT_BUDGET = 512 * 1024 * 1024


class RamCache:
    """Oldest-inserted handle is evicted first after the byte budget."""

    def __init__(self, budget: int = DEFAULT_BUDGET) -> None:
        self._budget = budget
        self._items: OrderedDict[str, ImageHandle] = OrderedDict()
        self._bytes = 0

    def get(self, key: str) -> ImageHandle | None:
        """Return a handle and mark it most-recent."""
        handle = self._items.get(key)
        if handle is None:
            return None
        self._items.move_to_end(key)
        return handle

    def put(self, key: str, handle: ImageHandle) -> None:
        """Insert or refresh a handle, then evict until under budget."""
        existing = self._items.pop(key, None)
        if existing is not None:
            self._bytes -= len(existing.pixels)
        self._items[key] = handle
        self._bytes += len(handle.pixels)
        self._evict()

    def _evict(self) -> None:
        while self._bytes > self._budget and self._items:
            _, handle = self._items.popitem(last=False)
            self._bytes -= len(handle.pixels)
