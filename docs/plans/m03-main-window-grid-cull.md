# M03 — Main window, grid, cull, selected panel

## Goal

The v0 workflow on the new stack: virtualized grid, pick/reject/unrate, live selected panel, undo/redo, dark theme chrome, no modals on the hot path.

## Tests first

| Test module | Asserts |
| --- | --- |
| `tests/project/test_filter.py` | All / picks / rejects / unrated counts |
| `tests/catalog/test_cull.py` | P then X then U leaves no selection row; action_log has three ops |
| `tests/catalog/test_undo.py` | Undo pick restores unrated; redo restores pick |
| `tests/ui/test_photo_model.py` | `QAbstractListModel` (or a Qt-free `PhotoList` façade used by the model) updates rating roles |
| `tests/ui/test_shortcuts_map.py` | Default map contains P, X, U, Ctrl+Z, Ctrl+E |

UI tests that need widgets use `pytest-qt` and `QT_QPA_PLATFORM=offscreen`.

## Implementation

1. Replace the M02 preview `QLabel` with `QStackedWidget` (grid page only for now).
2. Native menu bar, slim top bar (filter chips, placeholder sync), status bar (filename + index).
3. Docks: selected (right, live), filmstrip (bottom, stub list), project tree (hidden).
4. `ui/grid.py` — `QListView` IconMode + model. Badges for pick/reject. Rejects 40% opacity. Placeholder pixmap until the imaging future lands.
5. `ui/selected.py` — vertical list, header `Picks N`, click emits `jump_to(photo_id)`, context menu remove / export-one (export-one no-ops until M05 with a banner).
6. `ui/actions.py` — QActions for every hotkey; tooltips `Action (shortcut)`.
7. Cull path: keypress → writer.submit + immediate in-memory model update (no waiting on SQLite flush).
8. First-run coach-mark overlay once (flag in app-data).
9. Inline error banner widget for scan/decode failures.

## Done when

- Keyboard P/X/U/arrows work with 500 synthetic JPEGs without UI stalls
- Selected panel count matches catalog picks after flush
- Undo/redo from menu and shortcuts
- Welcome still appears when no last project

## Pause

Stop for check-in. Do not start M04.
