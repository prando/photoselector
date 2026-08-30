from types import SimpleNamespace

from photoselector.imaging.decode import _embedded_thumb


def test_extract_thumb_path(monkeypatch: object) -> None:
    import io

    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (4, 4), "white").save(buf, format="JPEG")
    raw = SimpleNamespace(extract_thumb=lambda: SimpleNamespace(data=buf.getvalue()))
    image = _embedded_thumb(raw)
    assert image is not None
    assert image.size == (4, 4)
    del monkeypatch
