"""Helper components for the Score page UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QLayoutItem,
    QPushButton,
    QSizePolicy,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..themes.style_constants import (
    COURT_LABEL_STYLE,
    MATCH_HEADER_STYLE,
    SCORE_LABEL_STYLE,
    TEAM_ONE_STYLE,
    TEAM_TWO_STYLE,
)
from ..widgets.performance_plot import PerformanceBarChart, PerformancePlot
from .score_payload import ScorePayloadCodec, ScoreWidgets


@dataclass
class RankingRow:
    """Represents a single ranking entry."""

    place: int
    name: str
    points: int
    wins: int
    losses: int


@dataclass
class MatchCardResult:
    """Container for the created match card widget and its entries."""

    widget: QFrame
    entries: list[ScoreWidgets]


class MatchCardFactory:
    """Creates match cards for the matches section."""

    def __init__(self, on_score_changed: Callable[[], None]) -> None:
        self._on_score_changed = on_score_changed

    def create(self, match_index: int, teams: Sequence[tuple[str, ...]]) -> MatchCardResult:
        card = QFrame()
        card.setObjectName("matchCard")
        card.setMaximumWidth(720)
        card.setMinimumWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.addWidget(self._build_match_header(match_index))

        entries: list[ScoreWidgets] = []
        for team_index in range(0, len(teams), 2):
            team_one = tuple(teams[team_index])
            team_two = tuple(teams[team_index + 1])
            court_number = team_index // 2 + 1
            entry = self._create_game_row(card_layout, team_one, team_two, court_number)
            entries.append(entry)

        card_layout.addWidget(self._build_card_separator())
        return MatchCardResult(card, entries)

    def _create_game_row(
        self,
        parent_layout: QVBoxLayout,
        team_one: tuple[str, ...],
        team_two: tuple[str, ...],
        court_number: int,
    ) -> ScoreWidgets:
        row = QHBoxLayout()
        row.setSpacing(8)
        row_height = 32

        row.addWidget(self._build_court_label(court_number, row_height))
        row.addWidget(self._build_team_widget(team_one, team_two, row_height))
        row.addSpacing(12)

        score_widgets, score_layout = self._build_score_section(team_one, team_two, row_height)
        score_widgets.score_one.textChanged.connect(self._on_score_changed)
        score_widgets.score_two.textChanged.connect(self._on_score_changed)
        row.addLayout(score_layout)

        parent_layout.addLayout(row)
        return score_widgets

    @staticmethod
    def _build_match_header(index: int) -> QLabel:
        header = QLabel(f"Match {index}")
        header.setObjectName("matchHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setMinimumHeight(40)
        header.setStyleSheet(MATCH_HEADER_STYLE)
        return header

    @staticmethod
    def _build_card_separator() -> QFrame:
        separator = QFrame()
        separator.setObjectName("lineSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        return separator

    @staticmethod
    def _build_court_label(court_number: int, row_height: int) -> QLabel:
        court_label = QLabel(f"Court {court_number}:")
        court_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        court_label.setMinimumWidth(56)
        court_label.setMinimumHeight(row_height)
        court_label.setStyleSheet(COURT_LABEL_STYLE)
        return court_label

    @staticmethod
    def _build_team_widget(
        team_one: tuple[str, ...],
        team_two: tuple[str, ...],
        row_height: int,
    ) -> QWidget:
        team_container = QWidget()
        team_container.setMinimumHeight(row_height)
        team_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        team_layout = QHBoxLayout(team_container)
        team_layout.setContentsMargins(0, 0, 0, 0)
        team_layout.setSpacing(8)

        team_one_label = QLabel(" & ".join(team_one))
        team_one_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        team_one_label.setMinimumWidth(100)
        team_one_label.setMinimumHeight(row_height)
        team_one_label.setStyleSheet(TEAM_ONE_STYLE)
        team_one_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        vs_label = QLabel("vs")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setMinimumWidth(24)
        vs_label.setMinimumHeight(row_height)

        team_two_label = QLabel(" & ".join(team_two))
        team_two_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        team_two_label.setMinimumWidth(100)
        team_two_label.setMinimumHeight(row_height)
        team_two_label.setStyleSheet(TEAM_TWO_STYLE)
        team_two_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        team_layout.addWidget(team_one_label)
        team_layout.addWidget(vs_label)
        team_layout.addWidget(team_two_label)
        team_layout.setStretch(0, 1)
        team_layout.setStretch(1, 0)
        team_layout.setStretch(2, 1)

        return team_container

    @staticmethod
    def _build_score_section(
        team_one: tuple[str, ...],
        team_two: tuple[str, ...],
        row_height: int,
    ) -> tuple[ScoreWidgets, QHBoxLayout]:
        score_one = QLineEdit()
        score_one.setFixedWidth(44)
        score_one.setFixedHeight(row_height)
        score_one.setMaxLength(2)

        score_two = QLineEdit()
        score_two.setFixedWidth(44)
        score_two.setFixedHeight(row_height)
        score_two.setMaxLength(2)

        layout = QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        score_label = QLabel("Score")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setMinimumHeight(row_height)
        score_label.setStyleSheet(SCORE_LABEL_STYLE)
        score_label.setFixedWidth(64)

        dash_label = QLabel("-")
        dash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_label.setMinimumHeight(row_height)
        dash_label.setFixedWidth(16)

        layout.addWidget(score_label)
        layout.addWidget(score_one)
        layout.addWidget(dash_label)
        layout.addWidget(score_two)

        widgets = ScoreWidgets(
            team_one=team_one,
            team_two=team_two,
            score_one=score_one,
            score_two=score_two,
        )
        return widgets, layout


class MatchesSection:
    """Manages the match list area and score entry widgets."""

    def __init__(self, *, matches_layout: QVBoxLayout, on_score_changed: Callable[[], None]) -> None:
        self._layout = matches_layout
        self._factory = MatchCardFactory(on_score_changed)
        self._entries: list[ScoreWidgets] = []

    # -- Match cards --------------------------------------------------
    def populate(self, matches: Sequence[Sequence[tuple[str, ...]]]) -> None:
        self.clear()
        self._entries = []

        for index, match in enumerate(matches, start=1):
            result = self._factory.create(index, match)
            self._entries.extend(result.entries)
            self._layout.addWidget(result.widget)

        self._layout.addStretch(1)

    def clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                continue
            self._dispose_layout_item(item)

    @staticmethod
    def _dispose_layout_item(item: QLayoutItem) -> None:
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            return
        layout = item.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child is None:
                    continue
                MatchesSection._dispose_layout_item(child)

    # -- Score payload helpers ---------------------------------------
    def get_score_payload(self) -> list[dict[str, object]]:
        return ScorePayloadCodec.encode(self._entries)

    def apply_score_payload(self, payload: Sequence[Mapping[str, object]]) -> None:
        ScorePayloadCodec.apply(self._entries, payload)

    def iter_scores(self) -> Iterable[tuple[tuple[str, ...], tuple[str, ...], str, str]]:
        yield from ScorePayloadCodec.iter_scores(self._entries)


class RankingsSection:
    """Encapsulates rankings table population and filtering."""

    def __init__(self, *, search_input: QLineEdit, rank_table: QTableWidget) -> None:
        self._search_input = search_input
        self._rank_table = rank_table
        self._all_rankings: list[RankingRow] = []
        self._search_input.textChanged.connect(self.apply_filter)

    def update_rankings(self, ranked: Sequence[tuple[int, str, int, int, int]]) -> None:
        self._all_rankings = [RankingRow(*row) for row in ranked]
        self.apply_filter()

    def apply_filter(self) -> None:
        filtered = self._filtered_rankings(self._search_input.text())

        self._rank_table.setRowCount(len(filtered))
        highlight_names: set[str] = set()
        highlight_color = QColor("#fde68a") if highlight_names else None

        for row_index, entry in enumerate(filtered):
            place_item = QTableWidgetItem(str(entry.place))
            name_item = QTableWidgetItem(entry.name)
            points_item = QTableWidgetItem(str(entry.points))
            wins_item = QTableWidgetItem(str(entry.wins))
            losses_item = QTableWidgetItem(str(entry.losses))

            for table_item in (place_item, name_item, points_item, wins_item, losses_item):
                table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if highlight_color and entry.name in highlight_names:
                for table_item in (place_item, name_item, points_item, wins_item, losses_item):
                    table_item.setBackground(highlight_color)

            self._rank_table.setItem(row_index, 0, place_item)
            self._rank_table.setItem(row_index, 1, name_item)
            self._rank_table.setItem(row_index, 2, points_item)
            self._rank_table.setItem(row_index, 3, wins_item)
            self._rank_table.setItem(row_index, 4, losses_item)

        self._rank_table.resizeRowsToContents()

    def _filtered_rankings(self, query: str) -> list[RankingRow]:
        normalized = query.strip().casefold()
        if not normalized:
            return list(self._all_rankings)
        return [entry for entry in self._all_rankings if normalized in entry.name.casefold()]


class AnalyticsSection:
    """Controls the analytics tabs, player selection, and plotting."""

    def __init__(
        self,
        *,
        plot_canvas: PerformancePlot,
        bar_canvas: PerformanceBarChart,
        player_list: QListWidget,
        bar_player_list: QListWidget,
        plot_graph_button: QPushButton,
        plot_bars_button: QPushButton,
        line_toggle: QToolButton,
        analytics_tabs: QTabWidget,
        plot_tab_2: QWidget,
    ) -> None:
        self.plot_canvas = plot_canvas
        self.bar_canvas = bar_canvas
        self.player_list = player_list
        self.bar_player_list = bar_player_list
        self.plot_graph_button = plot_graph_button
        self.plot_bars_button = plot_bars_button
        self.line_toggle = line_toggle
        self.analytics_tabs = analytics_tabs
        self.plot_tab_2 = plot_tab_2

        self._history: list[Mapping[str, int]] = []
        self._all_players: list[str] = []
        self._graph_plot_dirty = False
        self._bar_plot_dirty = False
        self._cached_graph_players: tuple[str, ...] | None = None
        self._cached_bar_players: tuple[str, ...] | None = None
        self._last_refresh_origin: str | None = None

        self.player_list.setObjectName("playerPlotList")
        self.player_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.player_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.bar_player_list.setObjectName("playerPlotList")
        self.bar_player_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.bar_player_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.line_toggle.setObjectName("lineToggle")
        self.line_toggle.setToolTip("Draw lines connecting the plotted points.")
        self.line_toggle.hide()

        self.plot_graph_button.setObjectName("primaryButton")
        self.plot_graph_button.setToolTip("Render the performance graph for the selected players.")
        self.plot_graph_button.setMinimumWidth(140)
        self.plot_graph_button.setMaximumWidth(140)
        self.plot_graph_button.setEnabled(False)

        self.plot_bars_button.setObjectName("primaryButton")
        self.plot_bars_button.setToolTip("Render the cumulative performance bars for the selected players.")
        self.plot_bars_button.setMinimumWidth(140)
        self.plot_bars_button.setMaximumWidth(140)
        self.plot_bars_button.setEnabled(False)

    # -- External API ------------------------------------------------
    def update_plot_data(self, history: Iterable[Mapping[str, int]], players: Iterable[str]) -> None:
        self._history = list(history)
        self._all_players = list(players)
        self.ensure_player_lists()
        self.request_refresh("history-update", graph=True, bars=True)

    def set_players(self, players: Sequence[str], *, refresh: bool = True) -> None:
        self._all_players = list(players)
        self._populate_player_list(self.player_list, players)
        self._populate_player_list(self.bar_player_list, players)
        self.request_refresh("set-players", graph=True, bars=True, update_buttons=refresh)

    def handle_player_toggle(self) -> None:
        self.request_refresh("player-toggle", graph=True)

    def handle_bar_player_toggle(self) -> None:
        self.request_refresh("bar-toggle", bars=True)

    def active_plot_players(self) -> list[str]:
        if self._cached_graph_players is None:
            players = self._active_players_from(self.player_list)
            self._cached_graph_players = tuple(players)
        return list(self._cached_graph_players)

    def active_bar_players(self) -> list[str]:
        if self._cached_bar_players is None:
            players = self._active_players_from(self.bar_player_list)
            self._cached_bar_players = tuple(players)
        return list(self._cached_bar_players)

    def handle_line_toggle(self, enabled: bool) -> None:
        self.plot_canvas.set_connect_lines(enabled)
        if self.plot_canvas.isHidden():
            self.request_refresh("line-toggle", graph=True)
            return
        players = self.active_plot_players()
        if not players:
            self.request_refresh("line-toggle", graph=True)
            return
        self.plot_canvas.plot(self._history, players)
        self._graph_plot_dirty = False
        self.request_refresh("line-toggle")

    def handle_tab_changed(self, index: int) -> None:
        if self.analytics_tabs is None or self.plot_tab_2 is None:
            return
        widget = self.analytics_tabs.widget(index)
        if widget is self.plot_tab_2 and self.plot_bars_button is not None:
            self.plot_bars_button.setFocus()
        self.request_refresh("tab-change")

    def handle_plot_graph_button(self) -> None:
        if not self._graph_plot_dirty:
            return
        players = self.active_plot_players()
        if not players:
            return
        self.plot_canvas.plot(self._history, players)
        self.plot_canvas.setVisible(True)
        self.line_toggle.show()
        self._graph_plot_dirty = False
        self.request_refresh("plot-graph")

    def handle_plot_bars_button(self) -> None:
        if not self._bar_plot_dirty:
            return
        players = self._players_for_bars()
        if not players:
            return
        self.bar_canvas.plot(self._history, players)
        self.bar_canvas.setVisible(True)
        self.line_toggle.hide()
        self._bar_plot_dirty = False
        self.request_refresh("plot-bars")

    def apply_theme(self, is_dark: bool) -> None:
        self.plot_canvas.set_theme(is_dark)
        self.bar_canvas.set_theme(is_dark)

    def ensure_player_lists(self) -> bool:
        needs_refresh = False
        if self.player_list.count() != len(self._all_players):
            needs_refresh = True
        else:
            current_names = [self.player_list.item(i).text() for i in range(self.player_list.count())]
            if current_names != self._all_players:
                needs_refresh = True

        if self.bar_player_list.count() != len(self._all_players) and not needs_refresh:
            needs_refresh = True
        elif not needs_refresh:
            names = [self.bar_player_list.item(i).text() for i in range(self.bar_player_list.count())]
            if names != self._all_players:
                needs_refresh = True

        if needs_refresh:
            self.set_players(self._all_players, refresh=False)
        return needs_refresh

    def request_refresh(
        self,
        origin: str,
        *,
        graph: bool = False,
        bars: bool = False,
        update_buttons: bool = True,
    ) -> None:
        self._last_refresh_origin = origin
        if graph:
            self._graph_plot_dirty = True
            self._invalidate_player_cache(graph=True)
            if not self.plot_canvas.isHidden():
                self.plot_canvas.setVisible(False)
            self.line_toggle.hide()
        if bars:
            self._bar_plot_dirty = True
            self._invalidate_player_cache(bars=True)
            if not self.bar_canvas.isHidden():
                self.bar_canvas.setVisible(False)
        if update_buttons:
            self._update_plot_buttons()

    def _update_plot_buttons(self) -> None:
        graph_players = self.active_plot_players()
        bar_players = self.active_bar_players()
        self.plot_graph_button.setEnabled(self._graph_plot_dirty and bool(graph_players))
        self.plot_bars_button.setEnabled(self._bar_plot_dirty and bool(bar_players))

    def _players_for_bars(self) -> list[str]:
        return self.active_bar_players()

    def _active_players_from(self, widget: QListWidget) -> list[str]:
        selected: list[str] = []
        for index in range(widget.count()):
            item = widget.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        if selected:
            return selected
        return list(self._all_players)

    def _populate_player_list(self, widget: QListWidget, players: Sequence[str]) -> None:
        widget.blockSignals(True)
        widget.clear()
        for name in players:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(Qt.CheckState.Checked)
            widget.addItem(item)
        widget.blockSignals(False)
        self._update_player_list_width(widget)

    def _update_player_list_width(self, widget: QListWidget) -> None:
        if widget.count() == 0:
            widget.setMinimumWidth(110)
            widget.setMaximumWidth(110)
            return

        metrics = widget.fontMetrics()
        max_text_width = 0
        for index in range(widget.count()):
            item = widget.item(index)
            if item is None:
                continue
            max_text_width = max(max_text_width, metrics.horizontalAdvance(item.text()))

        style = widget.style()
        indicator = style.pixelMetric(QStyle.PixelMetric.PM_IndicatorWidth, None, widget)
        spacing = style.pixelMetric(QStyle.PixelMetric.PM_CheckBoxLabelSpacing, None, widget)
        if indicator < 0:
            indicator = 16
        if spacing < 0:
            spacing = 6
        frame = widget.frameWidth() * 2
        width = max_text_width + indicator + spacing + frame + 24
        width = max(width, 110)
        widget.setMinimumWidth(width)
        widget.setMaximumWidth(width)

    def _invalidate_player_cache(self, *, graph: bool = False, bars: bool = False) -> None:
        if graph:
            self._cached_graph_players = None
        if bars:
            self._cached_bar_players = None