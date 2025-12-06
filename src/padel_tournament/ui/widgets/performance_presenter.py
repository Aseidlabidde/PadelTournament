"""Rendering helpers for performance plots."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Mapping, Sequence

from matplotlib import colormaps, ticker
from matplotlib.axes import Axes


@dataclass(slots=True)
class LineRenderResult:
    """Metadata about the rendered line plot."""

    plotted_any: bool
    total_matches: int
    max_points: int


@dataclass(slots=True)
class BarRenderResult:
    """Metadata about the rendered bar chart."""

    ordered_players: list[str]
    max_total: int


class PerformancePresenter:
    """Delegates data preparation and plotting for performance charts."""

    def render_line(
        self,
        axes: Axes,
        history: Iterable[Mapping[str, int]],
        players: Iterable[str],
        *,
        connect_lines: bool,
        is_dark: bool,
    ) -> LineRenderResult:
        axes.clear()
        player_names = list(players)
        if not player_names:
            return LineRenderResult(plotted_any=False, total_matches=0, max_points=0)

        text_color = "#e2e8f0" if is_dark else "#1f2933"
        matches = list(history)
        total_matches = len(matches)
        x_points = {player: [0] for player in player_names}
        y_points = {player: [0] for player in player_names}
        totals = {player: 0 for player in player_names}

        for index, match in enumerate(matches, start=1):
            if not match:
                continue
            for player in player_names:
                totals[player] += match.get(player, 0)
                x_points[player].append(index)
                y_points[player].append(totals[player])

        plotted_any = False
        for player in player_names:
            xs = x_points[player]
            ys = y_points[player]
            if not xs or not ys:
                continue
            plotted_any = True
            points = axes.scatter(xs, ys, label=player, s=20)
            if connect_lines:
                colors = points.get_facecolor()
                color = tuple(colors[0]) if len(colors) else None
                line_kwargs = {"linewidth": 1.4, "alpha": 0.9}
                if color:
                    line_kwargs["color"] = color
                axes.plot(xs, ys, label="_nolegend_", **line_kwargs)

        axes.set_xlabel("Match #", fontsize=9, color=text_color)
        axes.set_ylabel("Cumulative Points", fontsize=9, color=text_color)
        axes.set_title("Player Performance", fontsize=11, color=text_color)

        max_points = max((max(values) for values in y_points.values() if values), default=0)
        padding = max(2, int(max_points * 0.1)) if max_points else 2
        upper = max(20, max_points + padding)
        axes.set_ylim(0, upper)
        if total_matches:
            axes.set_xlim(0, total_matches)
            axes.set_xticks(list(range(1, total_matches + 1)))
        else:
            axes.set_xlim(0, 1)
            axes.set_xticks([])
        axes.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        if plotted_any:
            legend = axes.legend(
                loc="upper left",
                bbox_to_anchor=(1.02, 1.0),
                borderaxespad=0.0,
                fontsize=8,
            )
            if legend:
                if is_dark:
                    legend.get_frame().set_facecolor("#1b273d")
                    legend.get_frame().set_edgecolor("#3b4a67")
                for text in legend.get_texts():
                    text.set_color(text_color)

        return LineRenderResult(plotted_any=plotted_any, total_matches=total_matches, max_points=max_points)

    def render_bars(
        self,
        axes: Axes,
        history: Iterable[Mapping[str, int]],
        players: Iterable[str],
        *,
        is_dark: bool,
    ) -> BarRenderResult:
        axes.clear()
        player_names = list(players)
        if not player_names:
            return BarRenderResult(ordered_players=[], max_total=0)

        text_color = "#e2e8f0" if is_dark else "#1f2933"

        matches = [match for match in history if match]
        totals = defaultdict(int)
        segments = defaultdict(list)

        for match in matches:
            for player, points in match.items():
                totals[player] += points
                segments[player].append(points)

        ordered_players = sorted(player_names, key=lambda name: totals.get(name, 0), reverse=True)
        if not ordered_players:
            return BarRenderResult(ordered_players=[], max_total=0)

        cmap = colormaps.get_cmap("tab20")
        total_matches = max((len(values) for values in segments.values()), default=0)

        tick_positions: list[int] = []
        tick_labels: list[str] = []

        for idx, player in enumerate(ordered_players):
            current_left = 0
            tick_positions.append(idx)
            tick_labels.append(player)
            player_segments = segments.get(player, [])
            if player_segments:
                for match_index, points in enumerate(player_segments):
                    if points <= 0:
                        continue
                    color = cmap(match_index / max(1, total_matches))
                    axes.barh(idx, points, left=current_left, color=color, edgecolor="#374151", linewidth=0.4)
                    current_left += points
            if current_left == 0:
                axes.barh(idx, 0.01, left=0, color="#94a3b8", edgecolor="#94a3b8", linewidth=0.2, alpha=0.4)

        max_total = max((totals.get(player, 0) for player in ordered_players), default=0)
        padding = max(5, int(max_total * 0.1)) if max_total else 5
        axes.set_xlim(0, max_total + padding)
        axes.set_xlabel("Cumulative Points", fontsize=9, color=text_color)
        axes.set_title("Cumulative Points by Player", fontsize=11, color=text_color)
        axes.set_yticks(tick_positions)
        axes.set_yticklabels(tick_labels, color=text_color)
        axes.set_ylim(-0.5, len(ordered_players) - 0.5)
        axes.invert_yaxis()
        axes.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        return BarRenderResult(ordered_players=ordered_players, max_total=max_total)
