"""Redact filesystem paths and account identifiers."""

from __future__ import annotations

import re

_PATH = re.compile(r"(?:[A-Za-z]:\\|/)[^\s:]+")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def scrub(text: str) -> str:
    """Replace absolute paths and emails."""
    cleaned = _PATH.sub("<path>", text)
    return _EMAIL.sub("<account>", cleaned)
