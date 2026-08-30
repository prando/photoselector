"""Default shortcut map. Editable later in Preferences → Keyboard."""

from __future__ import annotations

DEFAULTS: dict[str, str] = {
    "pick": "P",
    "reject": "X",
    "unrate": "U",
    "next": "Right",
    "prev": "Left",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Shift+Z",
    "grid": "G",
    "loupe": "L",
    "compare": "C",
    "open_loupe": "Return",
    "back": "Escape",
    "fullscreen": "F11",
    "filter_all": "Ctrl+1",
    "filter_picks": "Ctrl+2",
    "filter_rejects": "Ctrl+3",
    "filter_unrated": "Ctrl+4",
    "select_all": "Ctrl+A",
    "filmstrip": "F",
    "selected": "S",
    "tree": "Ctrl+0",
    "refresh": "Ctrl+R",
    "search": "Ctrl+F",
    "export": "Ctrl+E",
    "quit": "Ctrl+Q",
    "cheatsheet": "?",
    "fit": "Space",
    "sticky_11": "1",
}


def tooltip(action: str, label: str) -> str:
    """Tooltip in the form 'Action (shortcut)'."""
    shortcut = DEFAULTS.get(action, "")
    if not shortcut:
        return label
    return f"{label} ({shortcut})"
