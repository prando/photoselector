from tests.helpers import rec

from photoselector.catalog.models import Rating
from photoselector.drive.fake import FakeDriveClient
from photoselector.export.drive import push_copies, push_pick_list


def test_fake_drive_push() -> None:
    client = FakeDriveClient()
    records = [rec(1, "a.jpg", rating=Rating.PICK)]
    link = push_pick_list(client, "root", records)
    assert link.startswith("https://drive.example/")
    copied = push_copies(client, "root", ["id1"])
    assert "drive.example" in copied
