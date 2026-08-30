"""Culling workspace: grid, loupe, compare, docks, shortcuts."""

from __future__ import annotations

from concurrent.futures import Future
from pathlib import Path

from PySide6.QtCore import QModelIndex, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from photoselector.catalog.connection import open_reader
from photoselector.catalog.models import Rating
from photoselector.catalog.queries import PhotoRecord, load_photos
from photoselector.catalog.writer import Writer
from photoselector.imaging.buckets import snap_size
from photoselector.imaging.handle import ImageHandle
from photoselector.imaging.service import ImagingService, Priority
from photoselector.prefetch.window import plan_for
from photoselector.project.controller import CullController
from photoselector.project.filter import FilterMode
from photoselector.project.session import Session
from photoselector.project.store import PhotoList
from photoselector.ui.banner import Banner
from photoselector.ui.cheatsheet import Cheatsheet
from photoselector.ui.compare import CompareView, allowed
from photoselector.ui.export_dialog import export_copy, export_one, export_text
from photoselector.ui.filmstrip import FilmstripView
from photoselector.ui.grid import GridView
from photoselector.ui.loupe import LoupeView
from photoselector.ui.model import PhotoListModel
from photoselector.ui.pixmaps import to_pixmap
from photoselector.ui.selected import SelectedPanel
from photoselector.ui.shortcuts import DEFAULTS, tooltip
from photoselector.ui.zoom import press_one, press_space, press_z


class Workspace(QWidget):
    """Attached to the main window after a folder is opened."""

    _ready = Signal(int, int)

    def __init__(self, session: Session, window: QMainWindow) -> None:
        super().__init__()
        self._session = session
        self._window = window
        self._writer = Writer(session.db_path)
        self._store = PhotoList(load_photos(open_reader(session.db_path)))
        self._cull = CullController(self._store, self._writer)
        self._imaging = ImagingService(session.root / ".photoselector")
        self._model = PhotoListModel(self._store)
        self._pending: dict[
            tuple[int, int], tuple[Future[ImageHandle], int | None]
        ] = {}
        self._index = 0
        self._syncing = False
        self._ready.connect(self._on_ready)
        self._build()
        self._bind_keys()
        self._grid.selectionModel().currentChanged.connect(self._on_current)
        self._film.selectionModel().currentChanged.connect(self._on_current)
        self._refresh()
        self._prefetch()
        self._reveal()
        self._grid.setFocus()
        tick = QTimer(self)
        tick.timeout.connect(self._collect)
        tick.start(50)

    def close_project(self) -> None:
        """Flush catalog, stop decodes, and remove docks."""
        self._writer.close()
        self._imaging.close()
        self._drop_window_actions()
        for dock in getattr(self, "_docks_refs", ()):
            self._window.removeDockWidget(dock)
            dock.deleteLater()

    def _build(self) -> None:
        self._banner = Banner()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filename search")
        self._search.textChanged.connect(self._on_search)
        self._stack = QStackedWidget()
        self._grid = GridView(self._model)
        self._loupe = LoupeView(arrows_nudge=True)
        self._compare = CompareView(self._compare_pick)
        self._stack.addWidget(self._grid)
        self._stack.addWidget(self._loupe)
        self._stack.addWidget(self._compare)
        self._grid.doubleClicked.connect(lambda _i: self._show_loupe())
        self._loupe.nudge.connect(self._move)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._banner)
        root.addWidget(self._toolbar())
        root.addWidget(self._stack, 1)
        self._docks()

    def _toolbar(self) -> QToolBar:
        bar = QToolBar()
        for mode, label in (
            (FilterMode.ALL, "All"),
            (FilterMode.PICKS, "Picks"),
            (FilterMode.REJECTS, "Rejects"),
            (FilterMode.UNRATED, "Unrated"),
        ):
            button = QPushButton(label)
            button.setToolTip(tooltip(f"filter_{mode.value}", label))
            button.clicked.connect(lambda _c=False, m=mode: self._set_filter(m))
            bar.addWidget(button)
        bar.addWidget(self._search)
        for label, rating in (
            ("Pick", Rating.PICK),
            ("Reject", Rating.REJECT),
            ("Unrate", None),
        ):
            button = QPushButton(label)
            button.setToolTip(tooltip(label.lower(), label))
            button.clicked.connect(lambda _c=False, r=rating: self._rate(r))
            bar.addWidget(button)
        return bar

    def _docks(self) -> None:
        self._selected = SelectedPanel()
        self._selected.jump_to.connect(self._jump)
        self._selected.remove_requested.connect(self._unrate_id)
        self._selected.export_one.connect(self._export_one_id)
        right = QDockWidget("Selected", self._window)
        right.setWidget(self._selected)
        self._window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right)
        self._film = FilmstripView(self._model)
        self._film.clicked.connect(lambda idx: self._set_index(idx.row()))
        bottom = QDockWidget("Filmstrip", self._window)
        bottom.setWidget(self._film)
        self._window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom)
        tree = QDockWidget("Project", self._window)
        tree.setWidget(QLabel(str(self._session.root)))
        tree.hide()
        self._window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tree)
        self._docks_refs = (right, bottom, tree)

    def _bind_keys(self) -> None:
        """Window actions only — menu already owns ?, Ctrl+E, Ctrl+Q."""
        self._cull_actions: list[QAction] = []
        pairs: list[tuple[str, object]] = [
            ("pick", lambda: self._rate(Rating.PICK)),
            ("reject", lambda: self._rate(Rating.REJECT)),
            ("unrate", lambda: self._rate(None)),
            ("undo", self._undo),
            ("redo", self._redo),
            ("grid", lambda: self._stack.setCurrentIndex(0)),
            ("loupe", self._show_loupe),
            ("compare", self._show_compare),
            ("open_loupe", self._show_loupe),
            ("back", lambda: self._stack.setCurrentIndex(0)),
            ("fullscreen", self._fullscreen),
            ("filter_all", lambda: self._set_filter(FilterMode.ALL)),
            ("filter_picks", lambda: self._set_filter(FilterMode.PICKS)),
            ("filter_rejects", lambda: self._set_filter(FilterMode.REJECTS)),
            ("filter_unrated", lambda: self._set_filter(FilterMode.UNRATED)),
            ("search", self._search.setFocus),
        ]
        cull = self._window.menuBar().addMenu("&Cull")
        self._cull_menu = cull
        shown = {
            "pick": "Pick",
            "reject": "Reject",
            "unrate": "Unrate",
            "undo": "Undo",
            "redo": "Redo",
            "loupe": "Loupe",
            "grid": "Grid",
            "compare": "Compare",
        }
        for name, slot in pairs:
            action = QAction(tooltip(name, shown.get(name, name)), self._window)
            action.setShortcut(QKeySequence(DEFAULTS[name]))
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            action.triggered.connect(lambda _c=False, fn=slot: fn())
            self._window.addAction(action)
            self._cull_actions.append(action)
            if name in shown:
                cull.addAction(action)
        extras = [
            ("Space", self._space),
            ("Shift+Space", lambda: self._move(-1)),
            ("Z", self._hold_z),
            ("1", lambda: self._digit(1)),
            ("2", lambda: self._digit(2)),
            ("3", lambda: self._digit(3)),
            ("4", lambda: self._digit(4)),
        ]
        for seq, slot in extras:
            action = QAction(self._window)
            action.setShortcut(QKeySequence(seq))
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            action.triggered.connect(lambda _c=False, fn=slot: fn())
            self._window.addAction(action)
            self._cull_actions.append(action)

    def _drop_window_actions(self) -> None:
        for action in getattr(self, "_cull_actions", []):
            self._window.removeAction(action)
            action.deleteLater()
        self._cull_actions = []
        menu = getattr(self, "_cull_menu", None)
        if menu is not None:
            self._window.menuBar().removeAction(menu.menuAction())
            self._cull_menu = None

    def _rate(self, rating: Rating | None) -> None:
        record = self._current()
        if record is None:
            return
        self._cull.rate(record.id, rating)
        if self._store.filter is FilterMode.ALL and not self._store.search:
            self._model.notify_rating(record.id)
            self._selected.set_picks(self._store.picks())
            self._status()
        else:
            self._refresh()
        self._move(1)

    def _undo(self) -> None:
        if self._cull.undo():
            self._refresh()

    def _redo(self) -> None:
        if self._cull.redo():
            self._refresh()

    def _unrate_id(self, photo_id: int) -> None:
        self._cull.rate(photo_id, None)
        self._refresh()

    def _current(self) -> PhotoRecord | None:
        visible = self._store.visible()
        if not visible:
            return None
        self._index = min(self._index, len(visible) - 1)
        return visible[self._index]

    def _move(self, delta: int) -> None:
        self._select(self._index + delta)

    def _set_index(self, row: int) -> None:
        self._select(row)

    def _on_current(self, current: QModelIndex, _previous: QModelIndex) -> None:
        if self._syncing or not current.isValid():
            return
        self._select(current.row())

    def _select(self, row: int) -> None:
        visible = self._store.visible()
        if not visible:
            return
        self._index = min(max(0, row), len(visible) - 1)
        self._reveal()
        self._status()
        if self._stack.currentIndex() == 1:
            self._fill_loupe()
        self._prefetch()

    def _reveal(self) -> None:
        idx = self._model.index(self._index)
        if not idx.isValid():
            return
        self._syncing = True
        self._grid.setCurrentIndex(idx)
        self._grid.scrollTo(idx)
        self._film.setCurrentIndex(idx)
        self._film.scrollTo(idx)
        self._syncing = False

    def _jump(self, photo_id: int) -> None:
        for idx, record in enumerate(self._store.visible()):
            if record.id == photo_id:
                self._select(idx)
                self._show_loupe()
                return

    def _set_filter(self, mode: FilterMode) -> None:
        self._store.filter = mode
        self._index = 0
        self._refresh()
        self._prefetch()

    def _on_search(self, text: str) -> None:
        self._store.search = text
        self._index = 0
        self._refresh()

    def _refresh(self) -> None:
        self._model.reset_view()
        self._selected.set_picks(self._store.picks())
        self._status()
        self._reveal()

    def _status(self) -> None:
        visible = self._store.visible()
        if not visible:
            self._window.statusBar().showMessage("No photos in filter")
            return
        record = visible[self._index]
        taken = record.taken_at or "—"
        self._window.statusBar().showMessage(
            f"{self._index + 1}/{len(visible)}  {record.filename}  {taken}"
        )

    def _show_loupe(self) -> None:
        self._stack.setCurrentIndex(1)
        self._fill_loupe()

    def _fill_loupe(self) -> None:
        record = self._current()
        if record is None:
            return
        if self._paint_cached_loupe(record):
            return
        self._request(record, 2048, Priority.P0)

    def _paint_cached_loupe(self, record: PhotoRecord) -> bool:
        """Paint RAM/QPixmap hits now. True when 2048 is already in RAM."""
        cached = self._model.pixmap(record.id)
        if cached is not None and not cached.isNull():
            self._loupe.set_pixmap(cached)
        path = Path(record.path)
        for size in (2048, 1024):
            handle = self._imaging.ram_get(path, size, record.mtime_ns)
            if handle is None:
                continue
            self._apply_handle(record.id, handle, None, snap_size(size))
            if size == 2048:
                return True
        return False

    def _show_compare(self) -> None:
        rows = self._grid.selectionModel().selectedRows()
        records = [self._model.record_at(idx.row()) for idx in rows]
        chosen = [record for record in records if record is not None]
        if not allowed(len(chosen)):
            self._banner.show_message("Select 2–4 photos in the grid to compare")
            return
        self._compare.set_records(chosen)
        self._stack.setCurrentIndex(2)
        for index, record in enumerate(chosen):
            self._request(record, 1024, Priority.P1, tile=index)

    def _compare_pick(self, index: int) -> None:
        records = self._compare.records()
        if index >= len(records):
            return
        winner = records[index]
        self._cull.rate(winner.id, Rating.PICK)
        for record in records:
            if record.id != winner.id:
                self._cull.rate(record.id, Rating.REJECT)
        self._stack.setCurrentIndex(0)
        self._refresh()

    def _digit(self, slot: int) -> None:
        if self._stack.currentIndex() == 2:
            self._compare.pick(slot)
            return
        if slot == 1:
            self._loupe.apply_mode(press_one(self._loupe.mode))
            record = self._current()
            if record is not None:
                self._request(record, 4096, Priority.P0, full_raw=True)

    def _hold_z(self) -> None:
        self._loupe.apply_mode(press_z(self._loupe.mode))

    def _space(self) -> None:
        if self._stack.currentIndex() == 1:
            self._loupe.apply_mode(press_space(self._loupe.mode))
            return
        self._move(1)

    def _fullscreen(self) -> None:
        if self._window.isFullScreen():
            self._window.showNormal()
            return
        self._show_loupe()
        self._window.showFullScreen()

    def _export(self) -> None:
        dest = export_text(self, self._store.all_records())
        if dest is None:
            return
        copied = export_copy(self, self._store.all_records())
        extra = f" and copied to {copied}" if copied else ""
        self._banner.show_message(f"Wrote {dest}{extra}")

    def _export_one_id(self, photo_id: int) -> None:
        export_one(self, self._store.get(photo_id))

    def _cheatsheet(self) -> None:
        Cheatsheet(self).show()

    def _request(
        self,
        record: PhotoRecord,
        size: int,
        priority: Priority,
        *,
        full_raw: bool = False,
        tile: int | None = None,
    ) -> None:
        bucket = snap_size(size)
        slot = (record.id, bucket)
        if slot in self._pending:
            return
        path = Path(record.path)
        handle = self._imaging.ram_get(path, size, record.mtime_ns)
        if handle is not None:
            self._apply_handle(record.id, handle, tile, bucket)
            return
        future = self._imaging.request(
            path, size, priority, record.mtime_ns, full_raw=full_raw
        )
        self._pending[slot] = (future, tile)
        photo_id, snapped = record.id, bucket
        future.add_done_callback(lambda _f: self._emit_ready(photo_id, snapped))

    def _emit_ready(self, photo_id: int, bucket: int) -> None:
        self._ready.emit(photo_id, bucket)

    def _prefetch(self) -> None:
        visible = self._store.visible()
        plan = plan_for(self._index, len(visible))
        wanted: set[tuple[int, int]] = set()
        self._enqueue(visible, plan.p0, 1024, Priority.P0, wanted)
        self._enqueue(visible, plan.p1, 1024, Priority.P1, wanted)
        self._enqueue(visible, plan.p2, 256, Priority.P2, wanted)
        self._keep_current_wanted(visible, wanted)
        self._drop_outside(wanted)

    def _enqueue(
        self,
        visible: list[PhotoRecord],
        indices: frozenset[int],
        size: int,
        priority: Priority,
        wanted: set[tuple[int, int]],
    ) -> None:
        for idx in indices:
            record = visible[idx]
            self._request(record, size, priority)
            wanted.add((record.id, snap_size(size)))

    def _keep_current_wanted(
        self, visible: list[PhotoRecord], wanted: set[tuple[int, int]]
    ) -> None:
        if not visible:
            return
        if self._stack.currentIndex() == 1:
            record = visible[min(self._index, len(visible) - 1)]
            wanted.add((record.id, 2048))
        if self._stack.currentIndex() == 2:
            for record in self._compare.records():
                wanted.add((record.id, 1024))

    def _drop_outside(self, wanted: set[tuple[int, int]]) -> None:
        current = self._current()
        current_id = None if current is None else current.id
        stale = [slot for slot in self._pending if slot not in wanted]
        for slot in stale:
            photo_id, bucket = slot
            if photo_id == current_id:
                continue
            record = self._store.get(photo_id)
            self._imaging.cancel(Path(record.path), record.mtime_ns, bucket)
            self._pending.pop(slot, None)

    def _collect(self) -> None:
        for photo_id, bucket in list(self._pending):
            future, _tile = self._pending[(photo_id, bucket)]
            if future.done():
                self._on_ready(photo_id, bucket)

    def _on_ready(self, photo_id: int, bucket: int) -> None:
        item = self._pending.pop((photo_id, bucket), None)
        if item is None:
            return
        future, tile = item
        self._apply_future(photo_id, future, tile, bucket)

    def _apply_future(
        self,
        photo_id: int,
        future: Future[ImageHandle],
        tile: int | None,
        bucket: int,
    ) -> None:
        try:
            handle = future.result()
        except Exception:
            return
        self._apply_handle(photo_id, handle, tile, bucket)

    def _apply_handle(
        self,
        photo_id: int,
        handle: ImageHandle,
        tile: int | None,
        bucket: int,
    ) -> None:
        pixmap = to_pixmap(handle)
        if tile is not None:
            self._compare.set_pixmap(tile, pixmap)
            return
        self._model.set_pixmap(photo_id, pixmap)
        current = self._current()
        if current is None or current.id != photo_id:
            return
        if self._stack.currentIndex() == 1 and bucket >= 1024:
            self._loupe.set_pixmap(pixmap)
