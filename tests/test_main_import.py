from __future__ import annotations

from PySide6.QtWidgets import QApplication


def test_main_import_does_not_create_qapp() -> None:
    from photoselector import main as main_mod

    assert main_mod.main is not None
    assert QApplication.instance() is None
