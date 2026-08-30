# M01 — Scaffold, catalog, welcome

## Goal

A `uv`-managed package that launches a welcome window, opens a local folder, creates `<project>/.photoselector/`, and writes a versioned SQLite catalog of discovered photos. No grid, no decode pipeline, no Drive.

## Tests first

| Test module | Asserts |
| --- | --- |
| `tests/catalog/test_schema.py` | Fresh DB has `schema_version=1` and the five tables |
| `tests/catalog/test_migrations.py` | Applying `001_initial.sql` to an empty file is idempotent; a second open is a no-op |
| `tests/catalog/test_writer.py` | 100 upserts flush in one batch; a 250 ms idle flush lands; read-only connections cannot write |
| `tests/catalog/test_models.py` | Insert photo; pick/reject/unrate; unrate deletes the selection row |
| `tests/catalog/test_action_log.py` | 501 actions keep 500 rows; undo/redo cursor clamps |
| `tests/project/test_scan.py` | Scans jpeg/png/heic/raw extensions; skips `.photoselector` and non-images |
| `tests/project/test_hygiene.py` | Creates `.photoselector/`, `.gitignore`, `CACHEDIR.TAG` |
| `tests/project/test_recent.py` | Recent list is capped, most-recent first, persisted in a temp app-data dir |
| `tests/test_main_import.py` | `photoselector.main` imports without creating a `QApplication` |

Do **not** import `PySide6.QtWidgets` outside `ui/` and `main.py`. Catalog tests use the stdlib sqlite3 writer queue (the `QThread` wrapper is a thin adapter tested with `QCoreApplication` only if already required). Prefer a Qt-free `catalog.writer.Writer` so CI has no display.

## Implementation

1. `pyproject.toml` — package `photoselector` at `src/`, requires Python `>=3.12`, runtime deps: `pyside6`, `pillow`, `pillow-heif`, `rawpy`, `keyring`. Dev: `pytest`, `pytest-cov`, `ruff`, `black`, `mypy`, `pre-commit`. Scripts: `photoselector = photoselector.main:main`. Ruff McCabe max 8. Black line 88. mypy strict.
2. `uv lock`, `.pre-commit-config.yaml`, `ruff.toml` / tool tables in pyproject, `.gitignore` for `.venv`, `__pycache__`, `.photoselector`, `dist`, `.mypy_cache`.
3. Copy original script to `legacy/photo_v0.py` (byte-identical to upstream `photo.py`). `legacy/README.md` explains it is the 2017 Tkinter app and is not an entry point.
4. `src/photoselector/catalog/migrations/001_initial.sql` matching `docs/design.md` §4.2.
5. `catalog/connection.py` — `open_writer(path)` / `open_reader(path)` with WAL + `foreign_keys`.
6. `catalog/migrate.py` — apply numbered SQL files; set `schema_version`.
7. `catalog/writer.py` — queue + background thread; `submit(sql, params)`; flush on 100 items or 250 ms; `close()`.
8. `catalog/models.py` — `Photo`, `Rating`, `upsert_photo`, `set_rating`, `clear_rating`.
9. `catalog/action_log.py` — ring buffer helpers.
10. `project/scan.py` — recursive? **No.** v0 listed one directory. Design implies a project folder. Scan **non-recursive** of the project root plus one level of subfolders that are not `.photoselector`. Keep it simple; do not walk the entire tree.
11. `project/hygiene.py` — create cache dir, gitignore, platform exclude tags.
12. `project/recent.py` — JSON file under a caller-supplied app-data path.
13. `ui/themes/dark.qss` and `light.qss` — enough to style welcome (background, buttons, list).
14. `ui/welcome.py` — `QWidget` with Open folder, Open Google Drive (disabled, tooltip “Drive lands in M05”), recent list, drop target.
15. `ui/app.py` — `QMainWindow` that either shows welcome or, after open, a status line: `Scanned N photos` plus the project path. No grid yet.
16. `main.py` — `QApplication`, load dark theme, construct `App`.

## Done when

- `uv run pytest` passes
- `uv run ruff check src tests`
- `uv run black --check src tests`
- `uv run mypy src`
- `uv run python -m photoselector.main` opens the welcome window
- Opening a folder with images creates `.photoselector/catalog.db` with one `photo` row per supported file

## Pause

Stop here for check-in. Do not start M02.
