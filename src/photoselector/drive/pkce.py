"""PKCE verifier/challenge and loopback redirect URI."""

from __future__ import annotations

import base64
import hashlib
import os
import secrets


def make_verifier() -> str:
    """RFC 7636 code_verifier."""
    return secrets.token_urlsafe(64)[:128]


def challenge(verifier: str) -> str:
    """S256 code_challenge."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def loopback_uri(port: int) -> str:
    """System-browser loopback. Port is ephemeral at bind time."""
    return f"http://127.0.0.1:{port}/"


def configured() -> bool:
    """True when a desktop OAuth client id is in the environment."""
    return bool(os.environ.get("PHOTOSELECTOR_GOOGLE_CLIENT_ID"))
