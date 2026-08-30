"""Push pick list (and optional copies) through a DriveClient."""

from __future__ import annotations

from datetime import UTC, datetime

from photoselector.catalog.queries import PhotoRecord
from photoselector.drive.protocol import DriveClient
from photoselector.export.text import ordered_picks


def push_pick_list(
    client: DriveClient, folder_id: str, records: list[PhotoRecord]
) -> str:
    """Upload selected_photos.txt. Returns a share link."""
    picks = ordered_picks(records)
    body = "".join(f"{record.path}\n" for record in picks)
    uploaded = client.upload_text(folder_id, "selected_photos.txt", body)
    return client.share_link(uploaded.id)


def push_copies(client: DriveClient, folder_id: str, file_ids: list[str]) -> str:
    """Server-side copy into a timestamped subfolder. Returns share link."""
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    folder = client.mkdir(folder_id, f"picks-{stamp}")
    last = folder
    for file_id in file_ids:
        last = client.copy_file(file_id, folder.id, file_id)
    return client.share_link(last.id)
