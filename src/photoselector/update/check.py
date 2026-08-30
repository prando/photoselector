"""Compare the running version to a GitHub latest tag."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BannerState:
    """What the top bar should show."""

    visible: bool
    message: str
    url: str


def latest_newer(current: str, latest: str, releases_url: str) -> BannerState:
    """Show a banner only when latest > current and a URL is set."""
    if not releases_url.strip():
        return BannerState(False, "", "")
    if _tuple(latest) <= _tuple(current):
        return BannerState(False, "", "")
    message = f"Version {latest} is available"
    return BannerState(True, message, releases_url)


def _tuple(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in version.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)
