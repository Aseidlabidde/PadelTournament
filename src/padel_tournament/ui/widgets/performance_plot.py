"""Matplotlib canvas for plotting player performance."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Mapping

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PerformancePlot(FigureCanvas):
    """Matplotlib canvas that renders cumulative points for each player."""

    def __init__(self, parent=None, width: float = 5, height: float = 3, dpi: int = 100) -> None:
        figure = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = figure.add_subplot(111)
        super().__init__(figure)
        self.setParent(parent)
        self._is_dark = False
        self._apply_theme()

    def set_theme(self, is_dark: bool) -> None:
        if self._is_dark != is_dark:
            self._is_dark = is_dark
            self._apply_theme()
            self.draw()

    def plot(self, history: Iterable[Mapping[str, int]], players: Iterable[str]) -> None:
        self.axes.clear()
        self._apply_theme()
        players = list(players)
        if not players:
            self.draw()
            return

        cumulative = {player: [] for player in players}
        totals = {player: 0 for player in players}
        matches = list(history)
        for match in matches:
            for player in players:
                totals[player] += match.get(player, 0)
                cumulative[player].append(totals[player])

        x_values = list(range(1, len(matches) + 1))
        for player in players:
            self.axes.plot(x_values, cumulative[player], marker="o", linewidth=2, label=player)

        self.axes.set_xlabel("Match #", fontsize=9)
        self.axes.set_ylabel("Cumulative Points", fontsize=9)
        self.axes.set_title("Player Performance", fontsize=11)
        max_points = max((max(series) for series in cumulative.values() if series), default=0)
        padding = max(2, int(max_points * 0.1)) if max_points else 2
        upper = max(20, max_points + padding)
        self.axes.set_ylim(0, upper)
        if matches and players:
            legend = self.axes.legend(loc="upper left", fontsize=8)
            if legend and self._is_dark:
                legend.get_frame().set_facecolor("#1b273d")
                legend.get_frame().set_edgecolor("#3b4a67")
                for text in legend.get_texts():
                    text.set_color("#e2e8f0")
        self.draw()

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
