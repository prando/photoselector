"""Persisted recent-project list (most recent first, capped)."""

from __future__ import annotations

import json
from pathlib import Path

CAP = 12


class RecentStore:
    """JSON list of project directories under an injected app-data path."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def paths(self) -> list[Path]:
        """Return existing paths, most recent first."""
        return [path for path in self._raw() if path.is_dir()]

    def add(self, project: Path) -> None:
        """Move `project` to the front and drop entries past CAP."""
        resolved = project.resolve()
        items = [resolved]
        for old in self._raw():
            if old.resolve() != resolved:
                items.append(old)
        self._write(items[:CAP])

    def _raw(self) -> list[Path]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []
        return [Path(item) for item in data if isinstance(item, str)]

    def _write(self, items: list[Path]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [str(item) for item in items]
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
