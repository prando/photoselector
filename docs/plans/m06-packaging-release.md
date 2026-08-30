# M06 — Packaging, version banner, crash reporter

## Goal

Briefcase artifacts, signing runbooks, startup version-check banner, opt-in crash reporting. No in-app updater.

## Tests first

| Test module | Asserts |
| --- | --- |
| `tests/update/test_banner.py` | Empty `releases_url` → no fetch; newer tag → banner model; equal tag → hidden; paths not sent |
| `tests/privacy/test_scrub.py` | Absolute paths and emails are redacted from a sample traceback |
| `tests/privacy/test_reporter.py` | Null reporter is a no-op; opted-in reporter is not constructed when the pref is false |

## Implementation

1. Briefcase metadata in `pyproject.toml` (formal name PhotoSelector, bundle id `app.photoselector`).
2. `docs/release/macos.md` — universal dmg, Developer ID, minimal entitlements, notarytool, staple.
3. `docs/release/windows.md` — per-user MSI, Authenticode, winget manifest template.
4. `docs/release/linux.md` — AppImage, deb, rpm, GPG.
5. `update/check.py` — GET GitHub releases/latest on a thread; compare to `__version__`; UI banner with link.
6. `privacy/scrub.py` + `privacy/reporter.py` — `CrashReporter` protocol, `NullCrashReporter`, optional file dump under app-data when opted in. Preferences → Privacy checkbox.
7. README: `uv sync`, `uv run python -m photoselector.main`, how to open a folder, how to export, pointer to legacy.

## Done when

- `briefcase dev` launches the app
- Banner and scrub tests pass
- Release docs list exact commands; they do not require secrets in the repo

## Pause

v1 feature complete. Further work is sign-off and release engineering on real machines with certificates.
