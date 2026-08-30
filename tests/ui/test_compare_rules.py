from photoselector.ui.compare import allowed


def test_compare_requires_two_to_four() -> None:
    assert allowed(1) is False
    assert allowed(2) is True
    assert allowed(4) is True
    assert allowed(5) is False
