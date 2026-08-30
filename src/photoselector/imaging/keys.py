"""Disk/RAM cache keys."""

from __future__ import annotations

import hashlib
from pathlib import Path


def cache_key(path: Path | str, mtime_ns: int, size: int) -> str:
    """sha1 of path + mtime + bucket size."""
    payload = f"{path}:{mtime_ns}:{size}".encode()
    return hashlib.sha1(payload).hexdigest()
