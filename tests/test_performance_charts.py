"""Tests for the performance chart widgets."""
from __future__ import annotations

import math
import os
from collections import Counter
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from padel_tournament.ui.pages.score_page import ScorePage
from padel_tournament.ui.widgets import PerformanceBarChart, PerformancePlot


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _label_order(chart: PerformanceBarChart) -> list[str]:
    # Matplotlib stores y tick labels in display order; stripping to avoid padding.
    return [label.get_text().strip() for label in chart.axes.get_yticklabels()]


def test_bar_chart_orders_players_by_cumulative_score(qapp: QApplication) -> None:
    chart = PerformanceBarChart()
    history = [
        {"Alice": 6, "Bob": 2},
        {"Alice": 3, "Bob": 5, "Cara": 4},
        {"Cara": 5},
    ]
    players = ["Alice", "Bob", "Cara"]

    chart.plot(history, players)

    labels = _label_order(chart)
    assert labels == ["Alice", "Cara", "Bob"], "Players should be ordered by total descending"

    totals = Counter()
    for match in history:
        totals.update(match)
    expected = [player for player, _ in totals.most_common()]
    assert labels == expected, "Displayed order must match cumulative rank"


def test_bar_chart_renders_placeholder_for_scoreless_players(qapp: QApplication) -> None:
    chart = PerformanceBarChart()
    history = [
        {"Alice": 3},
        {"Alice": 4},
    ]
    players = ["Alice", "Dana"]

    chart.plot(history, players)

    patch_widths = [patch.get_width() for patch in chart.axes.patches]
    has_baseline = any(math.isclose(width, 0.01, rel_tol=0.05) for width in patch_widths)
    assert has_baseline, "Players without points should still receive a baseline bar"


def test_scatter_plot_limits_and_legend(qapp: QApplication) -> None:
    plot = PerformancePlot()
    history = [
        {"Alice": 4, "Bob": 2},
        {"Alice": 3, "Bob": 5},
    ]
    players = ["Alice", "Bob"]

    plot.plot(history, players)

    legend = plot.axes.get_legend()
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    assert labels == players

    x_limits = plot.axes.get_xlim()
    y_limits = plot.axes.get_ylim()
    assert math.isclose(x_limits[0], 0.0, rel_tol=1e-6)
    assert math.isclose(x_limits[1], len(history), rel_tol=1e-6)
    assert y_limits[0] == 0
    assert y_limits[1] >= 9


def _build_score_page() -> ScorePage:
    noop = MagicMock()
    page = ScorePage(
        on_score_changed=noop,
        on_update_rankings=noop,
        on_save=noop,
        on_load=noop,
        on_export_csv=noop,
        on_export_pdf=noop,
        on_back=noop,
        on_auto_toggle=noop,
    )
    return page


def test_score_page_plot_button_controls_render(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    page = _build_score_page()

    history = [
        {"Alice": 4, "Bob": 2},
        {"Alice": 1, "Bob": 3},
    ]
    players = ["Alice", "Bob"]
    page.update_plot(history, players)

    plot_calls = []

    def track_plot(*args, **kwargs):
        plot_calls.append((args, kwargs))

    monkeypatch.setattr(page.plot_canvas, "plot", track_plot)
    monkeypatch.setattr(page.bar_canvas, "plot", track_plot)

    assert page.plot_graph_button.minimumWidth() == page.plot_bars_button.minimumWidth()
    assert page.plot_graph_button.isEnabled()
    assert page.plot_bars_button.isEnabled()
    assert page.plot_canvas.isHidden()
    assert page.bar_canvas.isHidden()
    assert plot_calls == []

    page._handle_plot_graph_button()
    assert len(plot_calls) == 1
    assert not page.plot_graph_button.isEnabled()
    assert not page.plot_canvas.isHidden()

    plot_calls.clear()
    page.line_toggle.setChecked(True)
    assert len(plot_calls) == 1
    assert not page.plot_graph_button.isEnabled()

    plot_calls.clear()
    page.line_toggle.setChecked(False)
    assert len(plot_calls) == 1

    page.analytics_tabs.setCurrentWidget(page.plot_tab_2)
    assert page.plot_bars_button.isEnabled()
    plot_calls.clear()
    page._handle_plot_bars_button()
    assert len(plot_calls) == 1
    assert not page.plot_bars_button.isEnabled()
    assert not page.bar_canvas.isHidden()

    plot_calls.clear()
    page.analytics_tabs.setCurrentIndex(1)

    page._handle_player_toggle(page.player_list.item(0))
    assert page.plot_graph_button.isEnabled()
    assert not page.plot_bars_button.isEnabled()
    assert page.plot_canvas.isHidden()
    assert not page.bar_canvas.isHidden()
    assert plot_calls == []

    page._handle_bar_player_toggle(page.bar_player_list.item(0))
    assert page.plot_graph_button.isEnabled()
    assert page.plot_bars_button.isEnabled()
    assert page.bar_canvas.isHidden()

    page.analytics_tabs.setCurrentIndex(1)
    page._handle_plot_graph_button()
    assert len(plot_calls) == 1
    page.analytics_tabs.setCurrentWidget(page.plot_tab_2)
    plot_calls.clear()
    page._handle_plot_bars_button()
    assert len(plot_calls) == 1
    plot_calls.clear()

