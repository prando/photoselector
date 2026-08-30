from photoselector.privacy.scrub import scrub


def test_scrub_path_and_email() -> None:
    text = "crash in /Users/ada/Pics/x.jpg for ada@example.com"
    cleaned = scrub(text)
    assert "/Users" not in cleaned
    assert "ada@example.com" not in cleaned
    assert "<path>" in cleaned
    assert "<account>" in cleaned
