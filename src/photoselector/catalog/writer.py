"""Dedicated catalog writer thread with 250 ms / 100-write batching."""

from __future__ import annotations

import sqlite3
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from queue import Empty, Queue
from threading import Event, Thread

from photoselector.catalog.connection import open_writer
from photoselector.catalog.migrate import migrate

_BATCH = 100
_INTERVAL = 0.25

_Job = tuple[str, str, tuple[object, ...], Event | None]


class Writer:
    """Queue SQL writes onto one background connection."""

    def __init__(
        self,
        path: Path,
        *,
        batch_size: int = _BATCH,
        interval: float = _INTERVAL,
        on_commit: Callable[[int], None] | None = None,
    ) -> None:
        self._path = path
        self._batch_size = batch_size
        self._interval = interval
        self._on_commit = on_commit
        self._queue: Queue[_Job] = Queue()
        self._thread = Thread(target=self._run, name="catalog-writer", daemon=True)
        self._thread.start()

    def submit(self, sql: str, params: Sequence[object] = ()) -> None:
        """Enqueue one statement. Does not wait for commit."""
        self._queue.put(("exec", sql, tuple(params), None))

    def flush(self) -> None:
        """Block until the current queue has been committed."""
        done = Event()
        self._queue.put(("flush", "", (), done))
        if not done.wait(timeout=5):
            raise TimeoutError("catalog writer flush timed out")

    def close(self) -> None:
        """Flush, stop the thread, and close the connection."""
        self.flush()
        self._queue.put(("stop", "", (), None))
        self._thread.join(timeout=5)

    def _run(self) -> None:
        conn = open_writer(self._path)
        try:
            migrate(conn)
            self._loop(conn)
        finally:
            conn.close()

    def _loop(self, conn: sqlite3.Connection) -> None:
        batch: list[tuple[str, tuple[object, ...]]] = []
        deadline: float | None = None
        while True:
            job = self._recv(batch, deadline)
            if job is None:
                self._commit(conn, batch)
                batch.clear()
                deadline = None
                continue
            cmd, sql, params, event = job
            if cmd == "stop":
                self._commit(conn, batch)
                return
            if cmd == "flush":
                self._commit(conn, batch)
                batch.clear()
                deadline = None
                if event is not None:
                    event.set()
                continue
            if not batch:
                deadline = time.monotonic() + self._interval
            batch.append((sql, params))
            if len(batch) >= self._batch_size:
                self._commit(conn, batch)
                batch.clear()
                deadline = None

    def _recv(
        self,
        batch: list[tuple[str, tuple[object, ...]]],
        deadline: float | None,
    ) -> _Job | None:
        timeout = _timeout(batch, deadline)
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            return None

    def _commit(
        self,
        conn: sqlite3.Connection,
        batch: list[tuple[str, tuple[object, ...]]],
    ) -> None:
        if not batch:
            return
        conn.execute("BEGIN")
        for sql, params in batch:
            conn.execute(sql, params)
        conn.execute("COMMIT")
        if self._on_commit is not None:
            self._on_commit(len(batch))


def _timeout(
    batch: list[tuple[str, tuple[object, ...]]],
    deadline: float | None,
) -> float | None:
    if not batch or deadline is None:
        return None
    return max(0.0, deadline - time.monotonic())
