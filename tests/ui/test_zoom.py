from photoselector.ui.zoom import (
    ZoomMode,
    is_one_to_one,
    press_one,
    press_space,
    press_z,
    release_z,
)


def test_zoom_state_machine() -> None:
    mode = ZoomMode.FIT
    mode = press_z(mode)
    assert is_one_to_one(mode)
    mode = release_z(mode)
    assert mode is ZoomMode.FIT
    mode = press_one(mode)
    assert mode is ZoomMode.STICKY_11
    mode = press_space(mode)
    assert mode is ZoomMode.FIT
