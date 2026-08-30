"""Loupe zoom state machine (pure)."""

from __future__ import annotations

from enum import Enum


class ZoomMode(Enum):
    """Fit, sticky 1:1, or momentary 1:1 while Z is held."""

    FIT = "fit"
    STICKY_11 = "sticky"
    MOMENTARY_11 = "momentary"


def press_z(mode: ZoomMode) -> ZoomMode:
    """Hold Z → momentary 1:1."""
    del mode
    return ZoomMode.MOMENTARY_11


def release_z(mode: ZoomMode) -> ZoomMode:
    """Release Z from momentary → fit. Sticky is unchanged."""
    if mode is ZoomMode.MOMENTARY_11:
        return ZoomMode.FIT
    return mode


def press_one(mode: ZoomMode) -> ZoomMode:
    """Sticky 1:1. Pressing 1 again stays sticky."""
    del mode
    return ZoomMode.STICKY_11


def press_space(_mode: ZoomMode) -> ZoomMode:
    """Space fits to window."""
    return ZoomMode.FIT


def is_one_to_one(mode: ZoomMode) -> bool:
    """RAW full decode is required in either 1:1 mode."""
    return mode in {ZoomMode.STICKY_11, ZoomMode.MOMENTARY_11}
