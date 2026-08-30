"""Compute P0–P2 index sets around the current photo."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Band(Enum):
    """Prefetch priority band."""

    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


@dataclass(frozen=True)
class PrefetchPlan:
    """Index sets for the current filter order."""

    p0: frozenset[int]
    p1: frozenset[int]
    p2: frozenset[int]

    def contains(self, index: int) -> bool:
        """True if index is in P0–P2."""
        return index in self.p0 or index in self.p1 or index in self.p2


def plan_for(current: int, count: int) -> PrefetchPlan:
    """P0 = current; P1 = ±1..4; P2 = ±5..12. Clamped to [0, count)."""
    if count <= 0:
        empty: frozenset[int] = frozenset()
        return PrefetchPlan(empty, empty, empty)
    index = min(max(0, current), count - 1)
    p0 = frozenset({index})
    p1 = _band(index, count, 1, 4) - p0
    p2 = _band(index, count, 5, 12) - p0 - p1
    return PrefetchPlan(p0, p1, p2)


def _band(index: int, count: int, start: int, end: int) -> frozenset[int]:
    found: set[int] = set()
    for delta in range(start, end + 1):
        low = index - delta
        high = index + delta
        if 0 <= low < count:
            found.add(low)
        if 0 <= high < count:
            found.add(high)
    return frozenset(found)
