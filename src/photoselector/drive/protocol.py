"""DriveClient surface. Implementations must not depend on ui/."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DriveFile:
    """A file or folder listing entry."""

    id: str
    name: str
    is_folder: bool


class DriveClient(Protocol):
    """One-way download / push. Never writes originals on Drive."""

    def list_folder(self, folder_id: str) -> list[DriveFile]:
        """Children of a folder."""

    def download(self, file_id: str, dest: Path) -> Path:
        """Download one file to dest (file path)."""

    def upload_text(self, folder_id: str, name: str, text: str) -> DriveFile:
        """Create a text file in folder."""

    def copy_file(self, file_id: str, dest_folder_id: str, name: str) -> DriveFile:
        """Server-side copy into dest_folder."""

    def mkdir(self, parent_id: str, name: str) -> DriveFile:
        """Create a folder."""

    def share_link(self, file_id: str) -> str:
        """Return a shareable URL."""
