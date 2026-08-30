from photoselector.ui.shortcuts import DEFAULTS, tooltip


def test_defaults_contain_cull_and_export() -> None:
    for key in ("pick", "reject", "unrate", "undo", "export"):
        assert key in DEFAULTS
    assert DEFAULTS["pick"] == "P"
    assert "Ctrl+E" in tooltip("export", "Export")
