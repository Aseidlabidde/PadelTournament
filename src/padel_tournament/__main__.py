"""Module executed when running ``python -m padel_tournament``."""

from __future__ import annotations

from .application import main


def run() -> None:
    """Launch the padel tournament application."""
    main()


if __name__ == "__main__":
    run()
