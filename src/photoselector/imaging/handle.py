"""Qt-free decoded image result."""

from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class ImageHandle:
    """Raw pixels plus size. UI blits this to QPixmap; disk may PNG-encode."""

    width: int
    height: int
    pixels: bytes
    channels: int = 3

    @property
    def png_bytes(self) -> bytes:
        """PNG encoding for the disk cache (not used on the GUI thread)."""
        mode = "RGBA" if self.channels == 4 else "RGB"
        image = Image.frombytes(mode, (self.width, self.height), self.pixels)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    @classmethod
    def from_image(cls, image: Image.Image) -> ImageHandle:
        """Copy pixels out of a PIL image. No PNG encode."""
        if image.mode == "RGBA":
            src = image
            channels = 4
        else:
            src = image.convert("RGB") if image.mode != "RGB" else image
            channels = 3
        src.load()
        return cls(src.width, src.height, src.tobytes(), channels)
