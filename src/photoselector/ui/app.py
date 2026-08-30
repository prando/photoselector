"""Main window: welcome or the culling workspace."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow

from photoselector.drive.pkce import configured
from photoselector.project.recent import RecentStore
from photoselector.project.session import Session, open_session
from photoselector.ui.cheatsheet import Cheatsheet
from photoselector.ui.shortcuts import tooltip
from photoselector.ui.theme import apply_theme
from photoselector.ui.welcome import WelcomePage
from photoselector.ui.workspace import Workspace


class App(QMainWindow):
    """Single window. Workspace attaches docks after open."""

    def __init__(self, app_data: Path) -> None:
        super().__init__()
        self._app_data = app_data
        self._recent = RecentStore(app_data / "recent.json")
        self._session: Session | None = None
        self._workspace: Workspace | None = None
        self.setWindowTitle("PhotoSelector")
        self.resize(1200, 800)
        self._build_menu()
        self._show_welcome()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self._action("Open folder…", self._choose_folder, "Ctrl+O"))
        drive = self._action("Open Google Drive folder…", self._drive)
        drive.setEnabled(configured())
        drive.setToolTip(
            "Drive sign-in is not configured"
            if not configured()
            else "Open Google Drive folder"
        )
        file_menu.addAction(drive)
        file_menu.addAction(self._action("Close project", self._show_welcome, "Ctrl+W"))
        export = self._action(tooltip("export", "Export…"), self._export, "Ctrl+E")
        file_menu.addAction(export)
        file_menu.addSeparator()
        file_menu.addAction(self._action(tooltip("quit", "Quit"), self.close, "Ctrl+Q"))
        view = self.menuBar().addMenu("&View")
        view.addAction(self._action("Dark theme", lambda: self._theme("dark")))
        view.addAction(self._action("Light theme", lambda: self._theme("light")))
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self._action("Keyboard shortcuts", self._cheatsheet, "?"))

    def maybe_reopen(self) -> None:
        """Reopen the most recent project when one exists."""
        last = last_project_path(self._app_data)
        if last is not None:
            self._open_path(last)

    def _action(
        self, text: str, slot: Callable[[], object], shortcut: str | None = None
    ) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
            action.setToolTip(f"{text} ({shortcut})")
        action.triggered.connect(lambda _checked=False, fn=slot: fn())
        return action

    def _show_welcome(self) -> None:
        if self._workspace is not None:
            self._workspace.close_project()
            self._workspace = None
        self._session = None
        page = WelcomePage(self._recent.paths())
        page.open_requested.connect(self._choose_folder)
        page.path_chosen.connect(self._open_path)
        self.setCentralWidget(page)
        self.statusBar().showMessage("Open a folder to start culling")

    def _choose_folder(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Open photo folder")
        if chosen:
            self._open_path(Path(chosen))

    def _open_path(self, path: Path) -> None:
        if self._workspace is not None:
            self._workspace.close_project()
        session = open_session(path)
        self._recent.add(path)
        self._session = session
        workspace = Workspace(session, self)
        self._workspace = workspace
        self.setCentralWidget(workspace)
        flag = self._app_data / "coach_seen"
        if not flag.exists():
            workspace._banner.show_message(
                "P pick · X reject · U unrate · arrows next · L loupe · Ctrl+E export"
            )
            flag.write_text("1", encoding="utf-8")

    def _export(self) -> None:
        if self._workspace is not None:
            self._workspace._export()

    def _drive(self) -> None:
        self.statusBar().showMessage(
            "Set PHOTOSELECTOR_GOOGLE_CLIENT_ID to enable Drive sign-in"
        )

    def _theme(self, name: str) -> None:
        app = self.window().windowHandle()
        from PySide6.QtWidgets import QApplication

        instance = QApplication.instance()
        if instance is not None:
            apply_theme(instance, name)  # type: ignore[arg-type]
        del app

    def _cheatsheet(self) -> None:
        Cheatsheet(self).show()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._workspace is not None:
            self._workspace.close_project()
        event.accept()


def last_project_path(app_data: Path) -> Path | None:
    """Return the most recent project directory, if it still exists."""
    recents = RecentStore(app_data / "recent.json").paths()
    return recents[0] if recents else None
