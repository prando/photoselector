"""Create .photoselector and keep caches out of backup / iCloud."""

from __future__ import annotations

import os
import sys
from pathlib import Path

CACHE_DIR = ".photoselector"
GITIGNORE = ".photoselector/\n"
CACHE_TAG = "Signature: 8a477f597d28d172789f06886806bc55\n# PhotoSelector cache\n"


def catalog_path(root: Path) -> Path:
    """Return `<project>/.photoselector/catalog.db`."""
    return root / CACHE_DIR / "catalog.db"


def prepare_project(root: Path) -> Path:
    """Create the cache directory, gitignore, and platform exclude markers."""
    cache = root / CACHE_DIR
    cache.mkdir(parents=True, exist_ok=True)
    _write_if_absent(root / ".gitignore", GITIGNORE)
    _write_if_absent(cache / "CACHEDIR.TAG", CACHE_TAG)
    _exclude_macos(cache)
    _exclude_windows(cache)
    return cache


def _write_if_absent(path: Path, text: str) -> None:
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def _exclude_macos(cache: Path) -> None:
    nosync = cache.with_name(f"{cache.name}.nosync")
    if sys.platform == "darwin" and not nosync.exists():
        try:
            nosync.symlink_to(cache.name)
        except OSError:
            return


def _exclude_windows(cache: Path) -> None:
    if os.name != "nt":
        return
    hidden = 0x02
    not_indexed = 0x2000
    try:
        import ctypes

        ctypes.windll.kernel32.SetFileAttributesW(  # type: ignore[attr-defined]
            str(cache), hidden | not_indexed
        )
    except (AttributeError, OSError):
        return
