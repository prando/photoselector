"""Decode JPEG/PNG/HEIC/RAW to an ImageHandle."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

from photoselector.imaging.handle import ImageHandle
from photoselector.imaging.orient import apply_orientation
from photoselector.project.scan import EXTENSIONS

_HEIF_READY = False


def decode_path(
    path: Path,
    bucket: int,
    *,
    full_raw: bool = False,
) -> ImageHandle:
    """Decode, orient, and fit to `bucket` on the long edge."""
    image = _open(path, full_raw=full_raw)
    image = apply_orientation(image)
    image = _fit(image, bucket)
    return ImageHandle.from_image(image)


def _open(path: Path, *, full_raw: bool) -> Image.Image:
    fmt = EXTENSIONS.get(path.suffix.lower())
    if fmt == "raw":
        return _open_raw(path, full_raw=full_raw)
    if fmt == "heic":
        _ensure_heif()
    return Image.open(path)


def _open_raw(path: Path, *, full_raw: bool) -> Image.Image:
    import rawpy

    with rawpy.imread(str(path)) as raw:
        if not full_raw:
            thumb = _embedded_thumb(raw)
            if thumb is not None:
                return thumb
        rgb = raw.postprocess()
    return Image.fromarray(rgb)


def _embedded_thumb(raw: object) -> Image.Image | None:
    extract = getattr(raw, "extract_thumb", None)
    if extract is None:
        return None
    try:
        thumb = extract()
    except Exception:
        return None
    data = getattr(thumb, "data", None)
    if not data:
        return None
    return Image.open(io.BytesIO(data))


def _ensure_heif() -> None:
    global _HEIF_READY
    if _HEIF_READY:
        return
    import pillow_heif

    pillow_heif.register_heif_opener()
    _HEIF_READY = True


def _fit(image: Image.Image, bucket: int) -> Image.Image:
    long_edge = max(image.size)
    if long_edge <= bucket:
        return image
    ratio = bucket / long_edge
    size = (max(1, int(image.width * ratio)), max(1, int(image.height * ratio)))
    return image.resize(size, Image.Resampling.LANCZOS)
