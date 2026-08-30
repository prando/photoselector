"""Desktop OAuth helpers. System browser only; no embedded webview."""

from __future__ import annotations

import os

from photoselector.drive.pkce import challenge, loopback_uri, make_verifier


def authorization_url(port: int, client_id: str | None = None) -> str:
    """Build a Google authorization URL with PKCE + drive.file scope."""
    ident = client_id or os.environ.get("PHOTOSELECTOR_GOOGLE_CLIENT_ID", "")
    verifier = make_verifier()
    params = (
        f"client_id={ident}"
        f"&redirect_uri={loopback_uri(port)}"
        "&response_type=code"
        "&scope=https://www.googleapis.com/auth/drive.file"
        "&code_challenge_method=S256"
        f"&code_challenge={challenge(verifier)}"
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"
