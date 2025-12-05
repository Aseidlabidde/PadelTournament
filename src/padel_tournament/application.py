"""High-level entry points for launching the application."""
from __future__ import annotations

from .ui.main_window import launch

__all__ = ["main"]


def main() -> None:
    """Entry point used by ``python -m padel_tournament``."""

    launch()
