from photoselector.update.check import latest_newer


def test_banner_rules() -> None:
    hidden = latest_newer("0.1.0", "1.0.0", "")
    assert hidden.visible is False
    newer = latest_newer("0.1.0", "1.2.0", "https://example/releases")
    assert newer.visible is True
    assert "1.2.0" in newer.message
    same = latest_newer("1.2.0", "1.2.0", "https://example/releases")
    assert same.visible is False
