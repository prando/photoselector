from photoselector.drive.pkce import challenge, loopback_uri, make_verifier


def test_pkce_and_loopback() -> None:
    verifier = make_verifier()
    assert 43 <= len(verifier) <= 128
    hashed = challenge(verifier)
    assert hashed != verifier
    assert loopback_uri(43721) == "http://127.0.0.1:43721/"
