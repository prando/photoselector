# M04 — Loupe, compare, filmstrip, filters

## Goal

Loupe and 2–4 tile compare, working filmstrip, filter chips / Ctrl+1–4, F11 fullscreen, filename search, stars and color labels, near-duplicate grouping worker.

## Tests first

| Test module | Asserts |
| --- | --- |
| `tests/ui/test_zoom.py` | Fit, sticky 1:1, momentary 1:1 state machine (pure) |
| `tests/prefetch/test_loupe.py` | 1:1 request sets `full_raw=True` for RAW paths |
| `tests/ui/test_compare_rules.py` | Compare refuses <2 or >4; key 1–4 picks that tile and rejects others |
| `tests/project/test_search.py` | Substring filter on filename |
| `tests/imaging/test_phash.py` | Two identical JPEGs share a group_id; a solid-black vs solid-white do not |

## Implementation

1. `ui/loupe.py` — `QGraphicsView` + pixmap item; wheel zoom at cursor; pan; Z hold; `1` sticky; Space fit; arrows in filter order.
2. `ui/compare.py` — 2–4 synced views; Esc → grid; requires grid multi-select.
3. Filmstrip dock becomes a horizontal virtualized strip bound to the same filter model.
4. Top-bar chips bind to `Ctrl+1–4`. `Ctrl+F` focuses a filename search field that filters the model.
5. Star keys and color labels (menu + optional number row if it does not collide with compare `1–4`; compare owns `1–4` while that view is active; loupe owns `1` for 1:1). Stars via menu `Photo → Stars` and keys `Ctrl+Shift+1..5`. Colors via `Photo → Label`.
6. Idle pHash worker writes `photo.phash` / `group_id`. Preference “Stack duplicates” off by default.
7. F11 toggles fullscreen loupe on the current screen.
8. Help → Keyboard shortcuts: searchable non-modal dialog. Preferences → Keyboard: edit bindings.
9. Remove any leftover M02 preview pane.

## Done when

- G/L/C/Enter/Esc switch views correctly
- Compare 1–4 pick/reject rule holds
- Filter + search compose (search within current rating filter)
- Duplicate worker groups identical fixtures

## Pause

Stop for check-in. Do not start M05.
