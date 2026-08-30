from photoselector.catalog.models import Format, Rating
from photoselector.catalog.queries import PhotoRecord


def rec(
    ident: int,
    name: str,
    *,
    rating: Rating | None = None,
    taken: str | None = None,
    path: str | None = None,
    fmt: Format = "jpeg",
) -> PhotoRecord:
    """Short PhotoRecord constructor for tests."""
    return PhotoRecord(
        ident,
        path or f"/{name}",
        name,
        1,
        1,
        fmt,
        taken,
        rating,
        None,
        None,
        0,
    )
