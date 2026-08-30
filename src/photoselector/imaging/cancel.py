"""Per-job cancellation."""

from __future__ import annotations

from threading import Event


class CancelToken:
    """Set from the UI thread; workers check `is_cancelled`."""

    def __init__(self) -> None:
        self._event = Event()

    def cancel(self) -> None:
        """Mark the job cancelled."""
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        """True after `cancel()`."""
        return self._event.is_set()
