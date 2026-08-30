"""64-bit average hash for near-duplicate grouping."""

from __future__ import annotations

from PIL import Image


def average_hash(image: Image.Image, size: int = 8) -> str:
    """Return a 16-char hex aHash."""
    small = image.convert("L").resize((size, size))
    pixels = [int(byte) for byte in small.tobytes()]
    average = sum(pixels) / len(pixels)
    bits = "".join("1" if pixel >= average else "0" for pixel in pixels)
    return f"{int(bits, 2):016x}"


def hamming(left: str, right: str) -> int:
    """Hamming distance of two hex hashes."""
    return bin(int(left, 16) ^ int(right, 16)).count("1")


def same_group(left: str, right: str, limit: int = 8) -> bool:
    """True when hashes are near-duplicates."""
    return hamming(left, right) <= limit
