from photoselector.imaging.buckets import snap_size


def test_snap_size_rounds_up() -> None:
    assert snap_size(1) == 256
    assert snap_size(256) == 256
    assert snap_size(257) == 512
    assert snap_size(2000) == 2048
    assert snap_size(9000) == 4096
