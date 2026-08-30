from __future__ import annotations

from pathlib import Path

from photoselector.project.recent import CAP, RecentStore


def test_recent_is_capped_and_most_recent_first(tmp_path: Path) -> None:
    store = RecentStore(tmp_path / "app" / "recent.json")
    created: list[Path] = []
    for index in range(CAP + 3):
        folder = tmp_path / f"p{index}"
        folder.mkdir()
        created.append(folder)
        store.add(folder)
    items = store.paths()
    assert len(items) == CAP
    assert items[0] == created[-1].resolve()
    assert created[0] not in items
