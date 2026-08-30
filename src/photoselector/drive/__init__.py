"""DriveClient protocol and fakes. Real Google client is lazy."""

from photoselector.drive.fake import FakeDriveClient
from photoselector.drive.protocol import DriveClient, DriveFile

__all__ = ["DriveClient", "DriveFile", "FakeDriveClient"]
