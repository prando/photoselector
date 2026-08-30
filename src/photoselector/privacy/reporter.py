"""CrashReporter protocol and the default no-op."""

from __future__ import annotations

from typing import Protocol

from photoselector.privacy.scrub import scrub


class CrashReporter(Protocol):
    """Optional crash sink. Must scrub before send."""

    def report(self, traceback_text: str) -> None:
        """Handle one traceback."""


class NullCrashReporter:
    """Default: telemetry off."""

    def report(self, traceback_text: str) -> None:
        """No-op."""
        del traceback_text


class FileCrashReporter:
    """Append a scrubbed traceback to a local file when opted in."""

    def __init__(self, path: object) -> None:
        self._path = path

    def report(self, traceback_text: str) -> None:
        """Append one scrubbed report."""
        from pathlib import Path

        target = Path(str(self._path))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            handle.write(scrub(traceback_text))
            handle.write("\n")
