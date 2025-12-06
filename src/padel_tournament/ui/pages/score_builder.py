"""Utility to wire ScorePage widgets and helper sections."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QHeaderView,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..loaders import load_ui
from ..themes.style_constants import TAB_BAR_STYLE
from ..widgets.performance_plot import PerformanceBarChart, PerformancePlot
from .score_components import AnalyticsSection, MatchesSection, RankingsSection


@dataclass(slots=True)
class ScorePageWidgets:
    """Collected widget references from the UI file."""

    update_button: QPushButton
    save_button: QPushButton
    load_button: QPushButton
    csv_button: QPushButton
    pdf_button: QPushButton
    back_button: QPushButton
    auto_checkbox: QCheckBox
    analytics_toggle: QToolButton
    line_toggle: QToolButton
    plot_graph_button: QPushButton
    plot_bars_button: QPushButton
    search_input: QLineEdit
    player_list: QListWidget
    bar_player_list: QListWidget
    rank_table: QTableWidget
    scroll_area: QScrollArea
    matches_layout: QVBoxLayout
    analytics_container: QWidget
    summary_frame: QFrame
    summary_stack: QStackedWidget
    analytics_page: QWidget
    analytics_tabs: QTabWidget
    plot_tab_2: QWidget
    analytics_cover: QWidget
    layout_stack: QStackedWidget
    desktop_container: QWidget
    mobile_container: QWidget
    mobile_layout: QVBoxLayout
    splitter: QSplitter
    plot_canvas: PerformancePlot
    bar_canvas: PerformanceBarChart


@dataclass(slots=True)
class ScorePageSections:
    matches: MatchesSection
    rankings: RankingsSection
    analytics: AnalyticsSection


class ScorePageBuilder:
    """Assembles ScorePage widgets, layout tweaks, and helper sections."""

    def __init__(self, page: QWidget) -> None:
        self._page = page

    def build(
        self,
        *,
        on_score_changed: Callable[[], None],
        matches_section: MatchesSection | None,
        rankings_section: RankingsSection | None,
        analytics_section: AnalyticsSection | None,
    ) -> tuple[ScorePageWidgets, ScorePageSections]:
        widgets = self._collect_widgets()
        self._configure_layout(widgets)
        sections = self._instantiate_sections(
            widgets,
            on_score_changed=on_score_changed,
            matches_section=matches_section,
            rankings_section=rankings_section,
            analytics_section=analytics_section,
        )
        return widgets, sections

    def _collect_widgets(self) -> ScorePageWidgets:
        page = self._page
        def require(widget_type: type, name: str):
            widget = page.findChild(widget_type, name)
            if widget is None:
                raise RuntimeError(f"score_page.ui is missing required widget '{name}'")
            return widget

        update_button = require(QPushButton, "update_button")
        save_button = require(QPushButton, "save_button")
        load_button = require(QPushButton, "load_button")
        csv_button = require(QPushButton, "csv_button")
        pdf_button = require(QPushButton, "pdf_button")
        back_button = require(QPushButton, "back_button")
        auto_checkbox = require(QCheckBox, "auto_checkbox")
        analytics_toggle = require(QToolButton, "analytics_toggle")
        scroll_area = require(QScrollArea, "scroll_area")
        matches_layout = require(QVBoxLayout, "matches_layout")
        layout_stack = require(QStackedWidget, "layout_stack")
        desktop_container = require(QWidget, "desktop_container")
        mobile_container = require(QWidget, "mobile_container")
        mobile_layout = require(QVBoxLayout, "mobile_layout")
        splitter = require(QSplitter, "splitter")
        analytics_slot = require(QWidget, "analytics_slot")

        summary_frame = QFrame()
        load_ui(summary_frame, "panels/score_analytics_panel.ui")

        slot_layout = analytics_slot.layout()
        if not isinstance(slot_layout, QVBoxLayout):
            slot_layout = QVBoxLayout(analytics_slot)
        slot_layout.setContentsMargins(0, 0, 0, 0)
        slot_layout.setSpacing(0)
        slot_layout.addWidget(summary_frame)

        def require_child(container: QWidget, widget_type: type, name: str):
            widget = container.findChild(widget_type, name)
            if widget is None:
                raise RuntimeError(f"{widget_type.__name__} '{name}' not found in analytics panel")
            return widget

        summary_stack = require_child(summary_frame, QStackedWidget, "summary_stack")
        analytics_page = require_child(summary_frame, QWidget, "analytics_page")
        analytics_tabs = require_child(summary_frame, QTabWidget, "analytics_tabs")
        plot_tab_2 = require_child(summary_frame, QWidget, "plot_tab_2")
        analytics_cover = require_child(summary_frame, QWidget, "analytics_cover")
        plot_graph_button = require_child(summary_frame, QPushButton, "plot_graph_button")
        plot_bars_button = require_child(summary_frame, QPushButton, "plot_bars_button")
        line_toggle = require_child(summary_frame, QToolButton, "line_toggle")
        search_input = require_child(summary_frame, QLineEdit, "search_input")
        player_list = require_child(summary_frame, QListWidget, "player_list")
        bar_player_list = require_child(summary_frame, QListWidget, "bar_player_list")
        rank_table = require_child(summary_frame, QTableWidget, "rank_table")
        plot_placeholder = require_child(summary_frame, QWidget, "plot_placeholder")
        plot2_placeholder = require_child(summary_frame, QWidget, "plot2_placeholder")

        plot_layout = plot_placeholder.layout()
        if not isinstance(plot_layout, QVBoxLayout):
            raise RuntimeError("plot_placeholder must use QVBoxLayout")
        plot_canvas = PerformancePlot(page, width=8, height=5, dpi=110)
        plot_canvas.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        plot_canvas.setMinimumSize(600, 320)
        plot_canvas.setMaximumWidth(600)
        plot_placeholder.setMinimumWidth(640)
        plot_placeholder.setMaximumWidth(640)
        plot_placeholder.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(plot_canvas)
        plot_canvas.setVisible(False)

        plot2_layout = plot2_placeholder.layout()
        if not isinstance(plot2_layout, QVBoxLayout):
            raise RuntimeError("plot2_placeholder must use QVBoxLayout")
        bar_canvas = PerformanceBarChart(page, width=6, height=4, dpi=110)
        bar_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        bar_canvas.setMinimumSize(420, 320)
        plot2_layout.setContentsMargins(0, 0, 0, 0)
        plot2_layout.addWidget(bar_canvas)
        bar_canvas.setVisible(False)

        return ScorePageWidgets(
            update_button=update_button,
            save_button=save_button,
            load_button=load_button,
            csv_button=csv_button,
            pdf_button=pdf_button,
            back_button=back_button,
            auto_checkbox=auto_checkbox,
            analytics_toggle=analytics_toggle,
            line_toggle=line_toggle,
            plot_graph_button=plot_graph_button,
            plot_bars_button=plot_bars_button,
            search_input=search_input,
            player_list=player_list,
            bar_player_list=bar_player_list,
            rank_table=rank_table,
            scroll_area=scroll_area,
            matches_layout=matches_layout,
            analytics_container=analytics_slot,
            summary_frame=summary_frame,
            summary_stack=summary_stack,
            analytics_page=analytics_page,
            analytics_tabs=analytics_tabs,
            plot_tab_2=plot_tab_2,
            analytics_cover=analytics_cover,
            layout_stack=layout_stack,
            desktop_container=desktop_container,
            mobile_container=mobile_container,
            mobile_layout=mobile_layout,
            splitter=splitter,
            plot_canvas=plot_canvas,
            bar_canvas=bar_canvas,
        )

    def _configure_layout(self, widgets: ScorePageWidgets) -> None:
        widgets.matches_layout.setContentsMargins(24, 16, 24, 32)
        widgets.matches_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        desktop_layout = widgets.desktop_container.layout()
        if isinstance(desktop_layout, QVBoxLayout):
            desktop_layout.setContentsMargins(0, 0, 0, 0)

        summary_layout = widgets.summary_frame.layout()
        if isinstance(summary_layout, QVBoxLayout):
            summary_layout.setContentsMargins(12, 12, 12, 24)
            summary_layout.setSpacing(12)

        filter_widget = self._page.findChild(QWidget, "filter_widget")
        if filter_widget:
            filter_layout = filter_widget.layout()
            if isinstance(filter_layout, QHBoxLayout):
                filter_layout.setContentsMargins(0, 5, 0, 5)

        bar_filter_widget = self._page.findChild(QWidget, "bar_player_filter_widget")
        if bar_filter_widget:
            bar_filter_layout = bar_filter_widget.layout()
            if isinstance(bar_filter_layout, QHBoxLayout):
                bar_filter_layout.setContentsMargins(0, 5, 0, 5)

        plot_grid = self._page.findChild(QGridLayout, "plotLayout")
        if plot_grid:
            plot_grid.setContentsMargins(16, 12, 16, 12)
            plot_grid.setColumnStretch(1, 1)
            plot_grid.setRowStretch(1, 1)
            plot_grid.setColumnStretch(2, 0)
            plot_grid.setColumnStretch(3, 0)

        plot2_grid = self._page.findChild(QGridLayout, "plot2Layout")
        if plot2_grid:
            plot2_grid.setContentsMargins(16, 12, 16, 12)
            plot2_grid.setHorizontalSpacing(16)
            plot2_grid.setVerticalSpacing(12)
            plot2_grid.setColumnStretch(1, 1)
            plot2_grid.setColumnStretch(2, 0)
            plot2_grid.setRowStretch(1, 1)

        cover_layout = self._page.findChild(QVBoxLayout, "coverLayout")
        if cover_layout:
            cover_layout.setContentsMargins(24, 24, 24, 24)

        widgets.mobile_layout.setContentsMargins(0, 0, 0, 0)

        title = self._page.findChild(QLabel, "title_label")
        if title:
            title.setObjectName("pageTitle")

        for label_name in ("plot_label", "plot2_label"):
            label = self._page.findChild(QLabel, label_name)
            if label:
                label.setObjectName("plotLabel")
                label.setStyleSheet("font-size: 14px; font-weight: 600; margin-bottom: 2px;")

        widgets.summary_frame.setObjectName("summaryPanel")
        widgets.summary_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widgets.summary_frame.setMinimumWidth(320)
        widgets.summary_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widgets.back_button.setObjectName("secondaryButton")

        widgets.analytics_toggle.setObjectName("analyticsToggle")
        widgets.analytics_toggle.setToolTip("Show or hide the rankings and performance chart panel.")
        widgets.line_toggle.setObjectName("lineToggle")
        widgets.line_toggle.setToolTip("Draw lines connecting the plotted points.")
        widgets.line_toggle.hide()

        widgets.plot_graph_button.setObjectName("primaryButton")
        widgets.plot_graph_button.setToolTip("Render the performance graph for the selected players.")
        widgets.plot_graph_button.setMinimumWidth(140)
        widgets.plot_graph_button.setMaximumWidth(140)
        widgets.plot_graph_button.setEnabled(False)

        widgets.plot_bars_button.setObjectName("primaryButton")
        widgets.plot_bars_button.setToolTip("Render the cumulative performance bars for the selected players.")
        widgets.plot_bars_button.setMinimumWidth(140)
        widgets.plot_bars_button.setMaximumWidth(140)
        widgets.plot_bars_button.setEnabled(False)

        widgets.player_list.setObjectName("playerPlotList")
        widgets.player_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        widgets.player_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        widgets.bar_player_list.setObjectName("playerPlotList")
        widgets.bar_player_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        widgets.bar_player_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        widgets.search_input.setClearButtonEnabled(True)
        widgets.search_input.setMinimumWidth(140)

        widgets.rank_table.setColumnCount(5)
        widgets.rank_table.setHorizontalHeaderLabels(["Place", "Player", "Points", "Wins", "Losses"])
        header = widgets.rank_table.horizontalHeader()
        if header is not None:
            for column in range(widgets.rank_table.columnCount()):
                header.setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        widgets.rank_table.setAlternatingRowColors(True)
        widgets.rank_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widgets.rank_table.verticalHeader().setVisible(False)
        widgets.rank_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        widgets.rank_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        widgets.scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        widgets.splitter.setStretchFactor(0, 7)
        widgets.splitter.setStretchFactor(1, 13)

        tab_bar = widgets.analytics_tabs.tabBar()
        tab_bar.setStyleSheet(TAB_BAR_STYLE)

    def _instantiate_sections(
        self,
        widgets: ScorePageWidgets,
        *,
        on_score_changed: Callable[[], None],
        matches_section: MatchesSection | None,
        rankings_section: RankingsSection | None,
        analytics_section: AnalyticsSection | None,
    ) -> ScorePageSections:
        matches = matches_section or MatchesSection(
            matches_layout=widgets.matches_layout,
            on_score_changed=on_score_changed,
        )
        rankings = rankings_section or RankingsSection(
            search_input=widgets.search_input,
            rank_table=widgets.rank_table,
        )
        analytics = analytics_section or AnalyticsSection(
            plot_canvas=widgets.plot_canvas,
            bar_canvas=widgets.bar_canvas,
            player_list=widgets.player_list,
            bar_player_list=widgets.bar_player_list,
            plot_graph_button=widgets.plot_graph_button,
            plot_bars_button=widgets.plot_bars_button,
            line_toggle=widgets.line_toggle,
            analytics_tabs=widgets.analytics_tabs,
            plot_tab_2=widgets.plot_tab_2,
        )
        return ScorePageSections(matches=matches, rankings=rankings, analytics=analytics)
