"""Matplotlib canvas for plotting player performance."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Mapping

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .performance_presenter import PerformancePresenter


class PerformancePlot(FigureCanvas):
    """Matplotlib canvas that renders cumulative points for each player."""

    def __init__(self, parent=None, width: float = 5, height: float = 3, dpi: int = 100) -> None:
        figure = Figure(figsize=(width, height), dpi=dpi, tight_layout=False)
        self.axes = figure.add_subplot(111)
        super().__init__(figure)
        self.setParent(parent)
        self._is_dark = False
        self._connect_lines = False
        self._presenter = PerformancePresenter()
        self._apply_theme()
        # Reserve space for axis labels and an external legend on the right.
        self.figure.subplots_adjust(bottom=0.24, left=0.14, right=0.78)

    def set_theme(self, is_dark: bool) -> None:
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self._apply_theme()
            self.draw()

    def plot(self, history: Iterable[Mapping[str, int]], players: Iterable[str]) -> None:
        self._apply_theme()
        self._presenter.render_line(
            self.axes,
            history,
            players,
            connect_lines=self._connect_lines,
            is_dark=self._is_dark,
        )
        self.draw()

    def set_connect_lines(self, enabled: bool) -> None:
        if self._connect_lines == enabled:
            return
        self._connect_lines = enabled

    def _apply_theme(self) -> None:
        if self._is_dark:
            figure_bg = "#0f172a"
            axis_bg = "#111c30"
            grid_color = "#1f2e4a"
            text_color = "#e2e8f0"
        else:
            figure_bg = "#f5f7fb"
            axis_bg = "#ffffff"
            grid_color = "#dbe3f5"
            text_color = "#1f2933"

        self.figure.set_facecolor(figure_bg)
        self.axes.set_facecolor(axis_bg)
        for spine in self.axes.spines.values():
            spine.set_color(text_color)
        self.axes.tick_params(colors=text_color, labelsize=8)
        self.axes.xaxis.label.set_color(text_color)
        self.axes.yaxis.label.set_color(text_color)
        self.axes.title.set_color(text_color)
        self.axes.grid(True, linestyle="--", linewidth=0.6, color=grid_color, alpha=0.8)


class PerformanceBarChart(FigureCanvas):
    """Matplotlib canvas that renders cumulative points as stacked bars."""

    def __init__(self, parent=None, width: float = 5, height: float = 3, dpi: int = 100) -> None:
        figure = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = figure.add_subplot(111)
        super().__init__(figure)
        self.setParent(parent)
        self._is_dark = False
        self._presenter = PerformancePresenter()
        self._apply_theme()
        self.figure.subplots_adjust(bottom=0.26, left=0.24)

    def set_theme(self, is_dark: bool) -> None:
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self._apply_theme()
            self.draw()

    def plot(self, history: Iterable[Mapping[str, int]], players: Iterable[str]) -> None:
        self._apply_theme()
        self._presenter.render_bars(self.axes, history, players, is_dark=self._is_dark)
        self.draw()

    def _apply_theme(self) -> None:
        if self._is_dark:
            figure_bg = "#0f172a"
            axis_bg = "#111c30"
            text_color = "#e2e8f0"
            grid_color = "#1f2e4a"
        else:
            figure_bg = "#f5f7fb"
            axis_bg = "#ffffff"
            text_color = "#1f2933"
            grid_color = "#dbe3f5"

        self.figure.set_facecolor(figure_bg)
        self.axes.set_facecolor(axis_bg)
        for spine in self.axes.spines.values():
            spine.set_color(text_color)
        self.axes.tick_params(colors=text_color, labelsize=8)
        self.axes.xaxis.label.set_color(text_color)
        self.axes.title.set_color(text_color)
        self.axes.grid(True, axis="x", linestyle="--", linewidth=0.6, color=grid_color, alpha=0.7)
