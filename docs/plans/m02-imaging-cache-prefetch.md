# M02 — Imaging, cache, prefetch

## Goal

`imaging.request(path, size, priority) -> Future[QPixmap]` with RAM+disk LRU, EXIF orientation in workers, RAW embedded thumbs, cancellable `QThreadPool`, and P0–P3 prefetch. Grid/loupe are still not built; a headless harness and a tiny preview pane on the post-open window prove the pipeline.

## Tests first

| Test module | Asserts |
| --- | --- |
| `tests/imaging/test_buckets.py` | Sizes snap to 256/512/1024/2048/4096 |
| `tests/imaging/test_cache_key.py` | Key changes when mtime or size bucket changes |
| `tests/cache/test_ram_lru.py` | Evicts oldest after byte budget |
| `tests/cache/test_disk_lru.py` | Writes JPEG bytes; evicts oldest atime past  budget |
| `tests/imaging/test_orient.py` | A JPEG with EXIF orientation 6 is decoded already rotated (worker helper, no widget) |
| `tests/imaging/test_request.py` | Future completes with a pixmap-like `ImageHandle` (width/height/bytes); second request is a RAM hit |
| `tests/imaging/test_cancel.py` | Cancelled token is not stored in RAM cache |
| `tests/imaging/test_raw_thumb.py` | When a tiny DNG/fixture exists, `extract_thumb` path is used for non-1:1 |
| `tests/prefetch/test_window.py` | Given index `i` and `n=30`, P0/P1/P2 sets match design; navigation cancels the old P1 |

`ImageHandle` is a Qt-free result (`width`, `height`, `png_bytes`) produced by workers. `ui` converts to `QPixmap` on the GUI thread. This keeps imaging testable without `QApplication`.

## Implementation

1. `imaging/buckets.py`, `imaging/keys.py`, `imaging/orient.py`
2. `cache/ram.py`, `cache/disk.py` — disk root is `<project>/.photoselector/`
3. `imaging/decode.py` — jpeg/png via Pillow; heic via pillow-heif; raw via rawpy extract_thumb unless `full_raw=True`
4. `imaging/pool.py` — thread pool `min(cpu, 8)`, `QAtomicInt` or `threading` cancel flag wrapped as `CancelToken`
5. `imaging/service.py` — `request()`: RAM → disk → submit decode
6. `prefetch/window.py` — pure functions for bands; `prefetch/engine.py` — subscribe to current index
7. Wire M01’s post-open window to request P0 for photo 0 and show it in a `QLabel` (temporary; removed in M03)

## Done when

- Opening a 50-image folder fills disk thumbs in the background
- Loupe-sized request for the first image appears without blocking the UI thread
- Tests cover cache hits, cancel, orientation, prefetch sets

## Pause

Stop for check-in. Do not start M03.
