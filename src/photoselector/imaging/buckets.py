"""Snap a requested edge length to a cache bucket."""

from __future__ import annotations

BUCKETS: tuple[int, ...] = (256, 512, 1024, 2048, 4096)


def snap_size(requested: int) -> int:
    """Return the smallest bucket that is >= requested, or 4096."""
    size = max(1, int(requested))
    for bucket in BUCKETS:
        if bucket >= size:
            return bucket
    return BUCKETS[-1]
