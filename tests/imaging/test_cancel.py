from photoselector.imaging.cancel import CancelToken
from photoselector.imaging.service import CancelledError


def test_cancelled_token() -> None:
    token = CancelToken()
    assert token.is_cancelled is False
    token.cancel()
    assert token.is_cancelled is True
    assert issubclass(CancelledError, RuntimeError)
