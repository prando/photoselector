# M05 — Export and Google Drive

## Goal

Three export flavors and Drive-backed offline projects. Originals never written.

## Tests first

| Test module | Asserts |
| --- | --- |
| `tests/export/test_text_list.py` | Picks ordered by taken_at then filename; unrated/rejects omitted |
| `tests/export/test_copy.py` | `copy2` preserves mtime; rename template `{index:04d}_{original}`; cancel stops mid-batch |
| `tests/export/test_drive_push.py` | FakeDriveClient receives list upload + optional files.copy into timestamped folder |
| `tests/drive/test_protocol.py` | FakeDriveClient satisfies DriveClient (list, download, upload, copy, share) |
| `tests/drive/test_pkce.py` | PKCE verifier/challenge shape; loopback redirect URI is 127.0.0.1 with ephemeral port |
| `tests/sync/test_download.py` | Fake listing downloads only new/changed files into the target folder |

No real network. Real `GoogleDriveClient` is a thin wrapper, skipped in CI unless `PHOTOSELECTOR_DRIVE_IT=1`.

## Implementation

1. `export/text.py`, `export/copy.py`, `export/drive.py`
2. `Ctrl+E` opens the export confirmation modal (allowed). Progress in the top bar, cancellable.
3. Selected-panel “Export this photo only” uses the same copy path with a one-id filter.
4. `drive/protocol.py` — `DriveClient`
5. `drive/fake.py` — in-memory
6. `drive/google.py` — googleapiclient + google-auth-oauthlib PKCE loopback; tokens in keyring
7. `drive/oauth.py` — system browser only
8. Welcome “Open Google Drive folder” enabled when client id is set; otherwise tooltip “Drive sign-in is not configured”
9. After OAuth: folder picker (Drive list in a dialog — this is consent/target, allowed), download to a local folder, mark project Drive-backed
10. Offline: cull works; push action disabled with tooltip
11. Scope `drive.file` only

## Done when

- Text and copy exports covered by tests and a manual fixture folder
- Fake Drive push + download tests pass
- Real client is importable and unused in default CI

## Pause

Stop for check-in. Do not start M06.
