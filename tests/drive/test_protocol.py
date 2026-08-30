from pathlib import Path

from photoselector.drive.fake import FakeDriveClient


def test_fake_satisfies_protocol(tmp_path: Path) -> None:
    client = FakeDriveClient()
    folder = client.mkdir("root", "pics")
    uploaded = client.upload_text(folder.id, "list.txt", "a.jpg\n")
    dest = tmp_path / "list.txt"
    client.download(uploaded.id, dest)
    assert dest.read_text() == "a.jpg\n"
    clone = client.copy_file(uploaded.id, folder.id, "copy.txt")
    assert clone.name == "copy.txt"
    assert client.list_folder("root")
    assert client.share_link(uploaded.id)
