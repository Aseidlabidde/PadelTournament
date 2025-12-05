"""Padel tournament manager package."""

from __future__ import annotations

__all__ = ["main"]


def main() -> int:
	"""Entry point for console scripts.

	Delayed import keeps PyQt bindings out of test collection on headless runners.
	"""

	from .application import main as _main

	return _main()
