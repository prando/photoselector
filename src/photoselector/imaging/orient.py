"""Apply EXIF orientation in the decode worker."""

from __future__ import annotations

from PIL import Image, ImageOps


def apply_orientation(image: Image.Image) -> Image.Image:
    """Honor EXIF orientation and drop the tag."""
    return ImageOps.exif_transpose(image) or image
