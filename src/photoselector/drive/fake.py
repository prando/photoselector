"""In-memory DriveClient for tests."""

from __future__ import annotations

from pathlib import Path

from photoselector.drive.protocol import DriveFile


class FakeDriveClient:
    """Stores blobs in a dict. No network."""

    def __init__(self) -> None:
        self.files: dict[str, tuple[DriveFile, bytes]] = {}
        self._n = 0
        root = DriveFile("root", "My Drive", True)
        self.files["root"] = (root, b"")

    def list_folder(self, folder_id: str) -> list[DriveFile]:
        """Children whose parent prefix matches (simple flat map)."""
        del folder_id
        return [meta for meta, _ in self.files.values() if meta.id != "root"]

    def download(self, file_id: str, dest: Path) -> Path:
        """Write stored bytes to dest."""
        _meta, data = self.files[file_id]
        dest.write_bytes(data)
        return dest

    def upload_text(self, folder_id: str, name: str, text: str) -> DriveFile:
        """Store a text blob."""
        del folder_id
        return self._put(name, False, text.encode())

    def copy_file(self, file_id: str, dest_folder_id: str, name: str) -> DriveFile:
        """Duplicate a blob."""
        del dest_folder_id
        _meta, data = self.files[file_id]
        return self._put(name, False, data)

    def mkdir(self, parent_id: str, name: str) -> DriveFile:
        """Create a folder entry."""
        del parent_id
        return self._put(name, True, b"")

    def share_link(self, file_id: str) -> str:
        """Synthetic share URL."""
        return f"https://drive.example/{file_id}"

    def _put(self, name: str, is_folder: bool, data: bytes) -> DriveFile:
        self._n += 1
        ident = f"id{self._n}"
        meta = DriveFile(ident, name, is_folder)
        self.files[ident] = (meta, data)
        return meta
