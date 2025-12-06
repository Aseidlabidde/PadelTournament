"""Helpers for loading Qt Designer .ui files at runtime."""
from __future__ import annotations

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Iterator

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


@contextmanager
def _ui_path(resource: str) -> Iterator[str]:
    package = "padel_tournament.ui.designer"
    ui_resource = resources.files(package).joinpath(resource)
    with resources.as_file(ui_resource) as path:
        yield str(Path(path))


def load_ui(widget: QWidget, resource: str) -> None:
    """Load the given .ui resource into *widget*.

    Parameters
    ----------
    widget:
        The widget instance that should be populated with the UI definition.
    resource:
        Relative path of the .ui file stored under ``padel_tournament/ui/designer``.
    """

    with _ui_path(resource) as ui_path:
        uic.loadUi(ui_path, widget)
