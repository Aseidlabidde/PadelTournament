"""Theme helpers for loading application stylesheets."""
from __future__ import annotations

from importlib import resources

__all__ = ["load_stylesheet", "LIGHT_THEME", "DARK_THEME"]


def load_stylesheet(theme_name: str) -> str:
    """Load a QSS stylesheet embedded in the package."""

    resource_name = f"{theme_name}.qss"
    try:
        with resources.open_text(__name__, resource_name, encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError as exc:  # pragma: no cover - defensive path
        raise ValueError(f"Unknown theme '{theme_name}'") from exc


LIGHT_THEME = "material_light"
DARK_THEME = "material_dark"
