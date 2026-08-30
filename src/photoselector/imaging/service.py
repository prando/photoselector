"""Single request API: RAM hit sync; disk/decode on a priority pool."""

from __future__ import annotations

import os
from concurrent.futures import Future
from dataclasses import dataclass
from enum import IntEnum
from itertools import count
from pathlib import Path
from queue import Empty, PriorityQueue
from threading import Event, Lock, Thread

from photoselector.cache.disk import DiskCache
from photoselector.cache.ram import RamCache
from photoselector.imaging.buckets import snap_size
from photoselector.imaging.cancel import CancelToken
from photoselector.imaging.decode import decode_path
from photoselector.imaging.handle import ImageHandle
from photoselector.imaging.keys import cache_key


class Priority(IntEnum):
    """Lower is more urgent (P0 current, P3 idle sweep)."""

    P0 = 0
    P1 = 1
    P2 = 2
    P3 = 3


@dataclass
class _Job:
    path: Path
    bucket: int
    token: CancelToken
    full_raw: bool
    future: Future[ImageHandle]
    priority: int
    started: bool = False


class ImagingService:
    """Cancellable decode service with two-tier cache."""

    def __init__(
        self,
        cache_root: Path,
        *,
        workers: int | None = None,
    ) -> None:
        self._ram = RamCache()
        self._disk = DiskCache(cache_root)
        pool = workers if workers is not None else min(os.cpu_count() or 1, 8)
        n_workers = max(1, pool)
        self._queue: PriorityQueue[tuple[int, int, str]] = PriorityQueue()
        self._jobs: dict[str, _Job] = {}
        self._lock = Lock()
        self._seq = count()
        self._stop = Event()
        self._threads: list[Thread] = []
        for index in range(n_workers):
            thread = Thread(target=self._loop, name=f"img-{index}", daemon=True)
            thread.start()
            self._threads.append(thread)

    def ram_get(self, path: Path, size: int, mtime_ns: int) -> ImageHandle | None:
        """Return a RAM hit without touching disk or the pool."""
        return self._ram.get(cache_key(path, mtime_ns, snap_size(size)))

    def request(
        self,
        path: Path,
        size: int,
        priority: Priority,
        mtime_ns: int,
        *,
        full_raw: bool = False,
    ) -> Future[ImageHandle]:
        """Return a future. P0 is dequeued before P1–P3."""
        bucket = snap_size(size)
        key = cache_key(path, mtime_ns, bucket)
        hit = self._ram.get(key)
        if hit is not None:
            return _done(hit)
        with self._lock:
            existing = self._jobs.get(key)
            if existing is not None and not existing.token.is_cancelled:
                self._requeue(key, existing, priority)
                return existing.future
            future: Future[ImageHandle] = Future()
            job = _Job(path, bucket, CancelToken(), full_raw, future, int(priority))
            self._jobs[key] = job
        self._queue.put((int(priority), next(self._seq), key))
        return future

    def cancel(self, path: Path, mtime_ns: int, size: int) -> None:
        """Cancel an in-flight decode for this key."""
        key = cache_key(path, mtime_ns, snap_size(size))
        with self._lock:
            job = self._jobs.get(key)
            if job is None:
                return
            job.token.cancel()
            if not job.started:
                self._jobs.pop(key, None)
                if not job.future.done():
                    job.future.set_exception(CancelledError(key))

    def close(self) -> None:
        """Stop workers."""
        self._stop.set()
        for _ in self._threads:
            self._queue.put((99, next(self._seq), ""))
        for thread in self._threads:
            thread.join(timeout=2)

    def _requeue(self, key: str, job: _Job, priority: Priority) -> None:
        urgent = int(priority)
        if urgent >= job.priority:
            return
        job.priority = urgent
        self._queue.put((urgent, next(self._seq), key))

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                _priority, _seq, key = self._queue.get(timeout=0.2)
            except Empty:
                continue
            if not key:
                return
            self._run(key)

    def _run(self, key: str) -> None:
        job = self._claim(key)
        if job is None:
            return
        handle = self._load(key, job)
        if handle is None:
            return
        self._ram.put(key, handle)
        self._finish(key, job, handle)

    def _claim(self, key: str) -> _Job | None:
        with self._lock:
            job = self._jobs.get(key)
            if job is None or job.future.done() or job.started:
                return None
            if job.token.is_cancelled:
                self._jobs.pop(key, None)
                if not job.future.done():
                    job.future.set_exception(CancelledError(key))
                return None
            job.started = True
            return job

    def _load(self, key: str, job: _Job) -> ImageHandle | None:
        handle = self._disk.get(key, job.bucket)
        if handle is not None:
            return handle
        if job.token.is_cancelled:
            self._fail(key, job)
            return None
        handle = decode_path(job.path, job.bucket, full_raw=job.full_raw)
        if job.token.is_cancelled:
            self._fail(key, job)
            return None
        self._disk.put(key, job.bucket, handle)
        return handle

    def _finish(self, key: str, job: _Job, handle: ImageHandle) -> None:
        with self._lock:
            if self._jobs.get(key) is job:
                self._jobs.pop(key, None)
        if not job.future.done():
            job.future.set_result(handle)

    def _fail(self, key: str, job: _Job) -> None:
        with self._lock:
            if self._jobs.get(key) is job:
                self._jobs.pop(key, None)
        if not job.future.done():
            job.future.set_exception(CancelledError(key))


class CancelledError(RuntimeError):
    """Raised when a decode is cancelled before cache store."""


def _done(handle: ImageHandle) -> Future[ImageHandle]:
    future: Future[ImageHandle] = Future()
    future.set_result(handle)
    return future
