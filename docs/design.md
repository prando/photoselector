# PhotoSelector Design

Modernize the 2017 Tkinter/Pillow culling script into a professional, keyboard-first desktop app. The user still leaves with a list of keeper photos (and an optional copy). Nothing in this document re-opens locked product decisions.

## 1. Product

PhotoSelector is a single-user, offline-first culling tool for sessions of 500–3000 photos. The operator opens a folder (or a Google Drive folder downloaded for offline use), works through a grid/loupe/compare loop, and exports picks.

**In scope**

- Fast pick / reject / unrate with a live selected gallery
- Star ratings (1–5) and color labels (red, yellow, green, blue, purple)
- Near-duplicate auto-grouping via perceptual hash
- Preview-only rotate (display transform; originals are never written)
- JPEG, PNG, HEIC natively; RAW via embedded JPEG, full decode only at 1:1
- Text-list export, filesystem copy export, Drive push (Drive-backed projects only)
- Dark theme default, light theme selectable, native HiDPI, keyboard-first
- Startup version-check banner that links to a GitHub release (no in-app updater)

**Out of scope (v1)**

- Photo editing (crop, exposure, color, export-time transforms)
- Lightroom / XMP sidecar read or write
- Multi-user concurrent culling
- Two-way Drive sync
- In-app auto-update

The original Tkinter app lives at `legacy/photo_v0.py` with `legacy/README.md`. It is not imported by the new package.

## 2. Users and primary loop

1. Launch → welcome (if no last project) or last project.
2. Open a local folder or sign in to Drive, pick a folder, download, cull offline.
3. Grid is the home view. Loupe is the precision view. Compare is 2–4 tiles.
4. `P` / `X` / `U` write the sparse selection catalog. The selected panel updates on every pick.
5. Filters (`Ctrl/Cmd 1–4`) change what the grid, filmstrip, and arrow keys walk.
6. Export writes a text list, copies files, or pushes to Drive. Originals are never modified.

## 3. Architecture

```
ui  →  project, prefetch, drive, sync, export
         ↓
      catalog, imaging, cache
```

Dependency rule: `ui/` may import everything. No module outside `ui/` imports `ui`. Every layer below `ui/` is testable without a windowing system. Qt Core types (`QPixmap`, `QThread`, `QThreadPool`, `QAtomicInt`) are allowed below `ui/` because they are not widgets.

Layout (PEP 517/518/621):

```
src/photoselector/
  main.py
  catalog/          schema, migrations, writer, models, queries
  imaging/          request API, decode workers, EXIF orientation
  cache/            RAM LRU + disk LRU
  prefetch/         priority windows P0–P3
  drive/            DriveClient protocol, real + fake
  sync/             one-way download / push helpers
  project/          scan, recent, ignore/exclude, settings
  export/           text list, copy, drive push
  ui/               window, views, docks, themes, shortcuts
```

Entry point: `python -m photoselector.main` via `uv run`.

## 4. Persistence

Path: `<project>/.photoselector/catalog.db`

SQLite settings: WAL, `synchronous=NORMAL`, `busy_timeout=5000`, `foreign_keys=ON`.

### 4.1 Connections

- One dedicated writer `QThread` owns the only read-write connection.
- UI and workers open read-only connections (`mode=ro`). They never write.
- The writer batches: flush every 250 ms **or** 100 queued writes, whichever first.

### 4.2 Schema (version 1)

`photo` — one row per file found by the scanner.

| Column | Notes |
| --- | --- |
| `id` | INTEGER PK |
| `path` | TEXT UNIQUE, absolute |
| `filename` | TEXT |
| `mtime_ns` | INTEGER |
| `size_bytes` | INTEGER |
| `taken_at` | TEXT ISO-8601 or NULL; EXIF DateTimeOriginal |
| `width`, `height` | INTEGER or NULL until first decode |
| `orientation` | INTEGER EXIF 1–8, default 1 |
| `format` | `jpeg` / `png` / `heic` / `raw` |
| `phash` | TEXT hex, filled by idle worker |
| `group_id` | INTEGER or NULL; near-duplicate group |
| `stars` | INTEGER 1–5 or NULL |
| `color` | `red\|yellow\|green\|blue\|purple` or NULL |
| `rotate_quarters` | INTEGER 0–3, preview-only |
| `scanned_at` | TEXT ISO-8601 |

`selection` — sparse. **No row means unrated.**

| Column | Notes |
| --- | --- |
| `photo_id` | PK, FK `photo(id)` ON DELETE CASCADE |
| `rating` | `pick` or `reject` |
| `updated_at` | TEXT ISO-8601 |

Stars and color live on `photo` so a file can be labeled without becoming a pick or reject. Unrate deletes the `selection` row only.

`action_log` — undo/redo ring buffer, 500 rows.

| Column | Notes |
| --- | --- |
| `id` | INTEGER PK |
| `seq` | INTEGER 0–499, UNIQUE |
| `op` | TEXT (`rate`, `unrate`, `stars`, `color`, `rotate`) |
| `payload` | TEXT JSON |
| `created_at` | TEXT ISO-8601 |

`project_data` — key/value (`schema_version`, `root_path`, `filter`, `last_photo_id`, `drive_folder_id`, …).

`drive_auth` — non-sensitive metadata only (`account_id`, `email`, `folder_id`, `folder_name`, `updated_at`). Refresh tokens go in the OS keychain via `keyring`, service `photoselector`, key `drive:<account_id>`.

### 4.3 Migrations

Numbered SQL files under `src/photoselector/catalog/migrations/`:

- `001_initial.sql` — tables and indexes above
- Future files are applied in lexical order

`schema_version` in `project_data` is the source of truth. Opening a catalog runs pending migrations on the writer thread before the UI reads.

Indexes: `photo(filename)`, `photo(taken_at)`, `photo(group_id)`, `selection(rating)`.

### 4.4 Undo / redo

Each cull or label mutation appends one `action_log` row (modulo 500). Undo applies the inverse from the current cursor; redo reapplies. The cursor is `project_data.undo_cursor`. Overflow drops the oldest row and clamps the cursor.

## 5. Imaging pipeline

Single request API:

```python
imaging.request(path: Path, size: int, priority: Priority) -> Future[QPixmap]
```

`size` is snapped to buckets `{256, 512, 1024, 2048, 4096}`. Callers pass the viewport’s longest edge; the pipeline chooses the next bucket up.

### 5.1 Cache

Two tiers, same key: `sha1(f"{path}:{mtime_ns}:{size}")`.

1. RAM LRU of `QPixmap` (budget: 512 MB default)
2. Disk LRU under `<project>/.photoselector/{thumbs,previews}` (budget: 4 GB default, preference)

`thumbs` holds 256/512. `previews` holds 1024/2048/4096. Evict oldest-atime files when the budget is exceeded.

### 5.2 Decode

- `QThreadPool` of size `min(os.cpu_count() or 1, 8)`
- Each job carries a `QAtomicInt` cancel token. Navigation cancels out-of-window jobs.
- EXIF orientation is applied **in the worker**, never on the UI thread.
- JPEG/PNG: Qt image reader, then orient.
- HEIC: `pillow-heif` → RGB → `QImage` → orient.
- RAW (`cr2`, `cr3`, `nef`, `arw`, `dng`, `raf`, `orf`): `rawpy.extract_thumb()` embedded JPEG for grid/loupe. Full libraw postprocess only when the request is 1:1 (hold `Z` or sticky `1`).
- Failures resolve the future with an error result; UI shows a corner badge, not a modal.

### 5.3 Prefetch windows

Around the current filtered index `i`:

| Band | Range | Size |
| --- | --- | --- |
| P0 | `i` | view size |
| P1 | `i±1…4` | view size |
| P2 | `i±5…12` | thumbnail (256) |
| P3 | remainder | thumbnail, only when the pool is idle |

On navigation, cancel jobs whose target is outside the new window. On project open, enqueue a low-priority thumbnail sweep (P3). Grid cells populate as futures complete. Loupe is usable as soon as P0 for the current photo lands.

## 6. Project folder hygiene

On first open of a folder, create `<project>/.photoselector/` and:

- `.gitignore` containing `.photoselector/`
- macOS: `com.apple.metadata:com_apple_backup_excludeItem` + `.nosync` sibling so Time Machine and iCloud skip the cache
- Windows: `FILE_ATTRIBUTE_HIDDEN` on `.photoselector` and `FILE_ATTRIBUTE_NOT_CONTENT_INDEXED`
- Linux: `CACHEDIR.TAG` plus a `user.xdg.cache` xattr when supported

Preferences live in the OS app-data dir (`QStandardPaths.AppDataLocation`), not in the project: recent projects, theme, shortcut map, cache budget, last project path, crash-reporting opt-in.

## 7. UI

Single `QMainWindow`.

- **Central:** `QStackedWidget` — Grid, Loupe, Compare
- **Docks:** filmstrip (bottom, visible), selected (right, visible), project tree (hidden by default)
- **Menu:** native menu bar; every action that has a shortcut appears here
- **Top bar:** filter chips (All / Picks / Rejects / Unrated), sync status, cancellable export progress, version-check banner
- **Status bar:** EXIF taken-at, filename, `index / count` in the current filter
- **Welcome:** shown when there is no last project (preference can force it). Actions: open local folder, open Google Drive folder, recent projects, folder drop target

No modal dialogs on cull hot paths. Errors are inline banners or cell badges. Modals are limited to: initial folder pick, Drive OAuth consent (system browser + loopback), export target confirmation, export permission errors.

### 7.1 Grid

`QListView` in `IconMode`, virtualized via a `QAbstractListModel` over the current filter. Multi-select with Shift/Cmd. Pick/reject corner badges. Rejects paint at 40% opacity. Enter opens loupe on the current item.

### 7.2 Loupe

`QGraphicsView` + `QGraphicsPixmapItem`. Wheel-zoom at cursor. Hold `Z` for momentary 1:1. Press `1` for sticky 1:1. `Space` fits to window. Drag pans. Arrows move in filter order. `F11` fullscreen on the current display.

### 7.3 Compare

Requires 2–4 photos selected in the grid. Shows a 2–4 tile grid of synced `QGraphicsView`s (shared zoom/pan). Keys `1`–`4` pick that tile and auto-reject the others. `Esc` returns to grid.

### 7.4 Selected panel

Live vertical thumbnail list. Header: `Picks N`. Updates on every `P`. Click jumps the current index and switches to loupe. Context menu: “Remove from selection”, “Export this photo only”.

### 7.5 Theme and timing

- `ui/themes/dark.qss` (default), `ui/themes/light.qss`
- Native HiDPI (`AA_UseHighDpiPixmaps`, Qt 6 default scaling)
- Event loop targets 60/120 Hz; cull actions are synchronous catalog writes (queued) plus immediate model updates so buttons never wait on decode
- First-run coach-mark overlay on the selected panel and filter chips (once; stored in app-data)

### 7.6 Keyboard

Modifier: `Meta` on macOS, `Ctrl` elsewhere (`Qt.ControlModifier` already does this if we use `QKeySequence.StandardKey` plus `Ctrl+` sequences).

| Action | Shortcut |
| --- | --- |
| Pick | `P` |
| Reject | `X` |
| Unrate | `U` |
| Next | `Right`, `Space` (grid/compare) |
| Prev | `Left`, `Shift+Space` |
| Home / End | `Home`, `End` |
| Undo / Redo | `Ctrl+Z`, `Ctrl+Shift+Z` |
| Grid / Loupe / Compare | `G`, `L`, `C` |
| Open loupe | `Enter` |
| Back | `Esc` |
| Fullscreen loupe | `F11` |
| Filter All / Picks / Rejects / Unrated | `Ctrl+1` … `Ctrl+4` |
| Select all in filter | `Ctrl+A` |
| Toggle filmstrip / selected / tree | `F`, `S`, `Ctrl+0` |
| Refresh | `Ctrl+R` |
| Filename search | `Ctrl+F` |
| Export | `Ctrl+E` |
| Quit | `Ctrl+Q` |
| Cheatsheet | `?` |
| Momentary 1:1 / sticky 1:1 / fit | `Z` (hold), `1`, `Space` (loupe) |

Grid selection: Shift+click / Shift+arrow extend, Ctrl/Cmd+click toggle.

Every shortcut is discoverable three ways: native menu, tooltip `Action (shortcut)`, and a searchable non-modal **Help → Keyboard shortcuts** cheatsheet. Shortcuts are editable in Preferences → Keyboard (stored in app-data). Defaults restore from a frozen map in `ui/shortcuts.py`.

## 8. Export

All three flavors are pure catalog reads. Originals are never modified.

1. **Text list** — absolute paths of picks, ordered by `taken_at` ascending, filename fallback. UTF-8, one path per line.
2. **Copy** — `shutil.copy2` into a confirmed target folder. Optional rename `{index:04d}_{original}`; default keeps original names. Cancellable progress in the top bar.
3. **Drive push** (Drive-backed projects only) — upload the text list into the source folder; optional server-side `files.copy` of picks into a timestamped subfolder. Toast with the shareable link. Disabled with a tooltip when offline.

## 9. Google Drive

- OAuth 2.0 desktop app, PKCE, loopback `127.0.0.1:<random>`, system browser only. No embedded webview.
- Scope: `drive.file` only. The app never modifies originals.
- After first sync, culling is fully offline. Push is disabled (tooltip) when offline.
- Welcome: “Sign in with Google Drive” → pick a Drive folder → download into a local target → open that folder as a Drive-backed project (`project_data.drive_folder_id` set).
- `DriveClient` protocol with `GoogleDriveClient` (`googleapiclient`) and `FakeDriveClient` for tests.

## 10. Ratings, labels, near-duplicates

- Stars `1`–`5` and colors are independent of pick/reject.
- Near-duplicates: aHash/pHash 64-bit, Hamming distance ≤ 8, computed by an idle worker. `group_id` is the smallest `photo.id` in the cluster. The grid can optionally stack groups (preference, off by default so v1 cull speed is unchanged). Compare is the intended review tool for a group.

## 11. Packaging and release

Briefcase, driven by `pyproject.toml`.

| Platform | Artifact | Signing |
| --- | --- | --- |
| macOS | universal `.dmg` (arm64 + x86_64) | Developer ID, minimal entitlements, `notarytool` + staple |
| Windows | per-user `.msi` (no admin) + winget manifest | Authenticode |
| Linux | `.AppImage` + `.deb` + `.rpm` | GPG |

v1 has no in-app updater. On startup, if a `releases_url` is configured, a GET of GitHub `releases/latest` may show a dismissible banner with the download link.

Telemetry is off. Preferences → Privacy has an opt-in crash-reporting toggle. When on, reports scrub filesystem paths and account identifiers. Implementation is a `CrashReporter` protocol: `NullCrashReporter` default, file-backed or vendor reporter only when opted in.

## 12. Tooling and quality

- Python 3.12+, PySide6 (Qt 6), managed by `uv` with `uv.lock`
- Ruff, Black, mypy `--strict`, pre-commit
- PEP 8 / 257 / 484 / 517 / 518 / 621 / 440
- McCabe complexity ≤ 8 and ≤ 60 lines per function
- TDD: tests land with or before each module
- `DriveClient` fakes in tests; no network in the default suite
- Layers below `ui/` have no widget imports

## 13. Milestone map

| ID | File | Outcome |
| --- | --- | --- |
| M01 | `docs/plans/m01-scaffold-catalog.md` | Tooling, legacy, catalog, project hygiene, welcome + open folder |
| M02 | `docs/plans/m02-imaging-cache-prefetch.md` | Request API, two-tier cache, decode pool, prefetch |
| M03 | `docs/plans/m03-main-window-grid-cull.md` | Main window, grid, cull keys, selected panel, undo |
| M04 | `docs/plans/m04-loupe-compare.md` | Loupe, compare, filmstrip, filters |
| M05 | `docs/plans/m05-export-drive.md` | Three export flavors, Drive OAuth + offline download |
| M06 | `docs/plans/m06-packaging-release.md` | Briefcase, signing docs, version banner, crash reporter |

Work pauses at the end of each milestone for check-in. This document is the source of truth for later milestones.

## 14. Defaults for underspecified details

These are locked here so implementation does not stall:

- Application name: **PhotoSelector**; Python package: `photoselector`
- Version at M01: `0.1.0`
- License: MIT (copyright retained from the 2017 project, 2026 modernization noted in README)
- `releases_url` defaults empty; banner hidden until packaging sets it
- Google OAuth client id/secret read from env `PHOTOSELECTOR_GOOGLE_CLIENT_ID` / `PHOTOSELECTOR_GOOGLE_CLIENT_SECRET`; unsigned builds show “Drive sign-in is not configured”
- Filename search is a case-insensitive substring filter over `photo.filename`
- Preview rotate is counterclockwise/clockwise 90° stored as `rotate_quarters`; decode workers apply it on top of EXIF orientation
- GIF/BMP from v0 are **not** added; supported formats are those listed in Formats
