"""Application entry: `python -m photoselector.main`."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from photoselector.ui.app import App
from photoselector.ui.theme import apply_theme


def app_data_dir() -> Path:
    """OS app-data location, created on first run."""
    from PySide6.QtCore import QStandardPaths

    location = QStandardPaths.StandardLocation.AppDataLocation
    root = QStandardPaths.writableLocation(location)
    path = Path(root) if root else Path.home() / ".photoselector"
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_app(argv: list[str] | None = None) -> QApplication:
    """Construct QApplication without starting the event loop."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        app = existing
    else:
        app = QApplication(argv if argv is not None else sys.argv)
    app.setApplicationName("PhotoSelector")
    app.setOrganizationName("PhotoSelector")
    apply_theme(app, "dark")
    return app


def main() -> int:
    """Launch the main window and run the Qt event loop."""
    assert sys.version_info < (3, 14), (
        "PhotoSelector requires Python 3.12 or 3.13 "
        f"(got {sys.version.split()[0]}). "
        "Pin with: uv python pin 3.13 && rm -rf .venv && uv sync --extra dev"
    )
    app = build_app()
    data = app_data_dir()
    window = App(data)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
