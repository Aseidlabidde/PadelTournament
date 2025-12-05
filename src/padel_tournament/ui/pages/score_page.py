"""Schedule and score management page."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..widgets.performance_plot import PerformancePlot


@dataclass
class ScoreEntry:
    team_one: tuple[str, ...]
    team_two: tuple[str, ...]
    score_one_edit: QLineEdit
    score_two_edit: QLineEdit


@dataclass
class RankingRow:
    place: int
    name: str
    points: int
    wins: int
    losses: int


class ScorePage(QWidget):
    """Displays generated matches, handles scoring, and shows rankings."""

    def __init__(
        self,
        *,
        on_score_changed: Callable[[], None],
        on_update_rankings: Callable[[], None],
        on_save: Callable[[], None],
        on_load: Callable[[], None],
        on_export_csv: Callable[[], None],
        on_export_pdf: Callable[[], None],
        on_back: Callable[[], None],
        on_auto_toggle: Callable[[bool], None],
    ) -> None:
        super().__init__()
        self._score_entries: list[ScoreEntry] = []
        self._on_score_changed = on_score_changed
        self._on_auto_toggle = on_auto_toggle
        self._cached_splitter_sizes: list[int] | None = None
        self._all_rankings: list[RankingRow] = []
        self._history: list[Mapping[str, int]] = []
        self._all_players: list[str] = []
        self._is_mobile_layout: bool = True

        self.player_list = QListWidget()
        self.player_list.setObjectName("playerPlotList")
        self.player_list.setMaximumWidth(180)
        self.player_list.itemChanged.connect(self._handle_player_toggle)

        self.update_button = QPushButton("Update Rankings")
        self.save_button = QPushButton("Save")
        self.load_button = QPushButton("Load")
        self.csv_button = QPushButton("Export CSV")
        self.pdf_button = QPushButton("Export PDF")
        self.back_button = QPushButton("Back to Setup")
        self.auto_checkbox = QCheckBox("Auto-update")
        self.analytics_toggle = QToolButton()
        self.analytics_toggle.setObjectName("analyticsToggle")
        self.analytics_toggle.setCheckable(True)
        self.analytics_toggle.setText("Show analytics")
        self.analytics_toggle.setToolTip("Show or hide the rankings and performance chart panel.")
        self.analytics_toggle.toggled.connect(self._toggle_analytics_panel)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search player…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._apply_rankings_filter)

        self.top_spin = QSpinBox()
        self.top_spin.setMinimum(0)
        self.top_spin.setMaximum(999)
        self.top_spin.setValue(0)
        self.top_spin.setPrefix("Top ")
        self.top_spin.setSpecialValueText("All players")
        self.top_spin.setToolTip("Limit the rankings table to the top N players (0 shows everyone).")
        self.top_spin.valueChanged.connect(self._apply_rankings_filter)

        self.update_button.clicked.connect(on_update_rankings)
        self.save_button.clicked.connect(on_save)
        self.load_button.clicked.connect(on_load)
        self.csv_button.clicked.connect(on_export_csv)
        self.pdf_button.clicked.connect(on_export_pdf)
        self.back_button.clicked.connect(on_back)
        self.auto_checkbox.stateChanged.connect(self._handle_auto_toggled)

        self.rank_table = QTableWidget(0, 5)
        self.rank_table.setHorizontalHeaderLabels(["Place", "Player", "Points", "Wins", "Losses"])
        header = self.rank_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rank_table.setAlternatingRowColors(True)
        self.rank_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rank_table.verticalHeader().setVisible(False)
        self.rank_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.rank_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.matches_host = QWidget()
        self.matches_layout = QVBoxLayout(self.matches_host)
        self.matches_layout.setSpacing(12)
        self.matches_layout.setContentsMargins(24, 16, 24, 32)
        self.matches_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.scroll_area.setWidget(self.matches_host)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.plot_canvas = PerformancePlot(self, width=8, height=5, dpi=110)
        self.plot_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.plot_canvas.setMinimumSize(520, 320)

        self.summary_stack: QStackedWidget | None = None
        self.analytics_cover: QWidget | None = None

        self._build_ui()

    # -- UI construction -------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Schedule & Scoring")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        for button in (self.update_button, self.save_button, self.load_button, self.csv_button, self.pdf_button):
            controls.addWidget(button)
        controls.addStretch(1)
        self.set_auto_checked(True)
        controls.addWidget(self.auto_checkbox)
        controls.addWidget(self.analytics_toggle)
        layout.addLayout(controls)

        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("summaryPanel")
        self.summary_frame.setMinimumWidth(320)

        summary_layout = QVBoxLayout(self.summary_frame)
        summary_layout.setSpacing(0)
        summary_layout.setContentsMargins(12, 12, 12, 24)

        self.analytics_tabs = QTabWidget()
        self.analytics_tabs.setObjectName("analyticsTabs")

        rankings_tab = QWidget()
        rankings_layout = QVBoxLayout(rankings_tab)
        rankings_layout.setSpacing(4)
        rankings_layout.setContentsMargins(16, 0, 16, 12)
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 5, 0, 5)
        filter_layout.setSpacing(8)
        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.top_spin)
        filter_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.search_input.setMinimumWidth(140)
        self.top_spin.setMinimumWidth(80)
        rankings_layout.addWidget(filter_widget)
        rankings_layout.addWidget(self.rank_table, 1)

        plot_tab = QWidget()
        plot_layout = QGridLayout(plot_tab)
        plot_layout.setContentsMargins(16, 12, 16, 12)
        plot_layout.setHorizontalSpacing(16)
        plot_layout.setVerticalSpacing(12)
        plot_label = QLabel("Graph players")
        plot_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        plot_layout.addWidget(plot_label, 0, 0, 1, 2)
        plot_layout.addWidget(self.player_list, 1, 0)
        plot_layout.addWidget(self.plot_canvas, 1, 1)
        plot_layout.setColumnStretch(0, 0)
        plot_layout.setColumnStretch(1, 1)
        plot_layout.setRowStretch(1, 1)

        self.analytics_tabs.addTab(rankings_tab, "Rankings")
        self.analytics_tabs.addTab(plot_tab, "Performance chart")

        self.summary_stack = QStackedWidget()
        self.summary_stack.setObjectName("analyticsStack")
        self.summary_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.summary_stack.addWidget(self.analytics_tabs)

        self.analytics_cover = QWidget()
        self.analytics_cover.setObjectName("analyticsCover")
        self.analytics_cover.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cover_layout = QVBoxLayout(self.analytics_cover)
        cover_layout.setContentsMargins(24, 24, 24, 24)
        cover_layout.addStretch(1)
        cover_label = QLabel("Analytics are hidden")
        cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover_label.setWordWrap(True)
        cover_label.setObjectName("analyticsCoverLabel")
        secondary_label = QLabel("Use 'Show analytics' to reveal rankings and charts again.")
        secondary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        secondary_label.setWordWrap(True)
        secondary_label.setObjectName("analyticsCoverHint")
        cover_layout.addWidget(cover_label)
        cover_layout.addSpacing(8)
        cover_layout.addWidget(secondary_label)
        cover_layout.addStretch(1)
        self.summary_stack.addWidget(self.analytics_cover)

        summary_layout.addWidget(self.summary_stack)

        self.layout_stack = QStackedWidget()
        self.layout_stack.setObjectName("scoreLayoutStack")

        self.desktop_container = QWidget()
        desktop_layout = QVBoxLayout(self.desktop_container)
        desktop_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 13)
        desktop_layout.addWidget(self.splitter)

        self.mobile_container = QWidget()
        self.mobile_layout = QVBoxLayout(self.mobile_container)
        self.mobile_layout.setContentsMargins(0, 0, 0, 0)
        self.mobile_layout.setSpacing(12)

        self.layout_stack.addWidget(self.desktop_container)
        self.layout_stack.addWidget(self.mobile_container)

        layout.addWidget(self.layout_stack)

        self.back_button.setObjectName("secondaryButton")
        layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

        self._apply_layout_mode(False)
        self.analytics_toggle.setChecked(True)
        if self.summary_stack is not None:
            self.summary_stack.setCurrentWidget(self.analytics_tabs)
        self._sync_analytics_cover_size()

    # -- Match cards -----------------------------------------------------
    def populate_matches(self, matches: Sequence[Sequence[tuple[str, ...]]]) -> None:
        self._clear_matches()
        self._score_entries = []

        for index, match in enumerate(matches, start=1):
            card = QFrame()
            card.setObjectName("matchCard")
            card.setMaximumWidth(720)
            card.setMinimumWidth(420)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(10)

            header = QLabel(f"Match {index}")
            header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setMinimumHeight(40)
            header.setStyleSheet("padding: 6px 0;")
            card_layout.addWidget(header)

            for team_index in range(0, len(match), 2):
                team_one = tuple(match[team_index])
                team_two = tuple(match[team_index + 1])
                court_number = team_index // 2 + 1
                entry = self._create_game_row(card_layout, team_one, team_two, court_number)
                self._score_entries.append(entry)

            separator = QFrame()
            separator.setObjectName("lineSeparator")
            separator.setFrameShape(QFrame.Shape.HLine)
            card_layout.addWidget(separator)

            self.matches_layout.addWidget(card)

        self.matches_layout.addStretch(1)

    def _clear_matches(self) -> None:
        while self.matches_layout.count():
            item = self.matches_layout.takeAt(0)
            if not item:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def _create_game_row(
        self,
        parent_layout: QVBoxLayout,
        team_one: tuple[str, ...],
        team_two: tuple[str, ...],
        court_number: int,
    ) -> ScoreEntry:
        row = QHBoxLayout()
        row.setSpacing(8)
        row_height = 32

        court_label = QLabel(f"Court {court_number}:")
        court_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        court_label.setMinimumWidth(56)
        court_label.setMinimumHeight(row_height)
        court_label.setStyleSheet("padding: 0 6px;")
        row.addWidget(court_label)

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
        team_one_label.setStyleSheet("color: #1d4ed8;")
        team_one_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        vs_label = QLabel("vs")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setMinimumWidth(24)
        vs_label.setMinimumHeight(row_height)

        team_two_label = QLabel(" & ".join(team_two))
        team_two_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        team_two_label.setMinimumWidth(100)
        team_two_label.setMinimumHeight(row_height)
        team_two_label.setStyleSheet("color: #b91c1c;")
        team_two_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        team_layout.addWidget(team_one_label)
        team_layout.addWidget(vs_label)
        team_layout.addWidget(team_two_label)
        team_layout.setStretch(0, 1)
        team_layout.setStretch(1, 0)
        team_layout.setStretch(2, 1)

        row.addWidget(team_container)

        row.addSpacing(12)

        score_one = QLineEdit()
        score_one.setFixedWidth(44)
        score_one.setFixedHeight(row_height)
        score_one.setMaxLength(2)
        score_two = QLineEdit()
        score_two.setFixedWidth(44)
        score_two.setFixedHeight(row_height)
        score_two.setMaxLength(2)

        score_one.textChanged.connect(self._on_score_changed)
        score_two.textChanged.connect(self._on_score_changed)

        score_label = QLabel("Score")
        score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_label.setMinimumHeight(row_height)
        score_label.setStyleSheet("padding: 0 6px;")
        row.addWidget(score_label)
        row.addWidget(score_one)
        dash_label = QLabel("-")
        dash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_label.setMinimumHeight(row_height)
        row.addWidget(dash_label)
        row.addWidget(score_two)

        parent_layout.addLayout(row)

        return ScoreEntry(team_one, team_two, score_one, score_two)

    def get_score_payload(self) -> list[dict[str, object]]:
        payload: list[dict[str, object]] = []
        for entry in self._score_entries:
            payload.append(
                {
                    "team1": list(entry.team_one),
                    "team2": list(entry.team_two),
                    "score1": entry.score_one_edit.text(),
                    "score2": entry.score_two_edit.text(),
                }
            )
        return payload

    def apply_score_payload(self, payload: Sequence[Mapping[str, object]]) -> None:
        for entry, saved in zip(self._score_entries, payload):
            entry.score_one_edit.setText(str(saved.get("score1", "")))
            entry.score_two_edit.setText(str(saved.get("score2", "")))

    def iter_scores(self) -> Iterable[tuple[tuple[str, ...], tuple[str, ...], str, str]]:
        for entry in self._score_entries:
            yield (
                entry.team_one,
                entry.team_two,
                entry.score_one_edit.text().strip(),
                entry.score_two_edit.text().strip(),
            )

    # -- Rankings --------------------------------------------------------
    def update_rankings_table(self, ranked: Sequence[tuple[int, str, int, int, int]]) -> None:
        self._all_rankings = [RankingRow(*row) for row in ranked]
        self.top_spin.setMaximum(len(self._all_rankings) if self._all_rankings else 0)
        self._apply_rankings_filter()

    def update_plot(self, history: Iterable[Mapping[str, int]], players: Iterable[str]) -> None:
        self._history = list(history)
        self._all_players = list(players)
        self._ensure_player_list()
        self._render_plot()

    # -- Auto update -----------------------------------------------------
    def set_auto_checked(self, enabled: bool) -> None:
        was_blocked = self.auto_checkbox.blockSignals(True)
        self.auto_checkbox.setChecked(enabled)
        self.auto_checkbox.blockSignals(was_blocked)

    def _handle_auto_toggled(self, state: int) -> None:
        self._on_auto_toggle(bool(state))

    def is_auto_enabled(self) -> bool:
        return self.auto_checkbox.isChecked()

    # -- Analytics visibility --------------------------------------------
    def _toggle_analytics_panel(self, _enabled: bool) -> None:
        self._update_summary_visibility()

    # -- Ranking filters --------------------------------------------------
    def _apply_rankings_filter(self) -> None:
        query = self.search_input.text().strip().casefold()
        top_limit = self.top_spin.value()
        filtered: list[RankingRow] = []
        for entry in self._all_rankings:
            if query and query not in entry.name.casefold():
                continue
            filtered.append(entry)
        if top_limit:
            filtered = filtered[:top_limit]

        self.rank_table.setRowCount(len(filtered))
        highlight_names = {row.name for row in self._all_rankings[:top_limit]} if top_limit else set()
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
                place_item.setBackground(highlight_color)
                name_item.setBackground(highlight_color)
                points_item.setBackground(highlight_color)
                wins_item.setBackground(highlight_color)
                losses_item.setBackground(highlight_color)
            self.rank_table.setItem(row_index, 0, place_item)
            self.rank_table.setItem(row_index, 1, name_item)
            self.rank_table.setItem(row_index, 2, points_item)
            self.rank_table.setItem(row_index, 3, wins_item)
            self.rank_table.setItem(row_index, 4, losses_item)

        self.rank_table.resizeRowsToContents()

    # -- Plot filters -----------------------------------------------------
    def set_players_for_plot(self, players: Sequence[str]) -> None:
        players = list(players)
        self._all_players = players
        self.player_list.blockSignals(True)
        self.player_list.clear()
        for name in players:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(Qt.CheckState.Checked)
            self.player_list.addItem(item)
        self.player_list.blockSignals(False)
        self._render_plot()

    def _handle_player_toggle(self, _item: QListWidgetItem) -> None:
        self._render_plot()

    def _active_plot_players(self) -> list[str]:
        selected: list[str] = []
        for index in range(self.player_list.count()):
            item = self.player_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        if selected:
            return selected
        return list(self._all_players)

    def _render_plot(self) -> None:
        active = [player for player in self._active_plot_players() if player in self._all_players]
        self.plot_canvas.plot(self._history, active)

    def _ensure_player_list(self) -> None:
        if self.player_list.count() == len(self._all_players):
            current_names = [self.player_list.item(i).text() for i in range(self.player_list.count())]
            if current_names == self._all_players:
                return
        self.set_players_for_plot(self._all_players)

    def apply_plot_theme(self, is_dark: bool) -> None:
        self.plot_canvas.set_theme(is_dark)
        self._render_plot()

    # -- Layout adjustments -----------------------------------------------
    def _apply_layout_mode(self, mobile: bool) -> None:
        previous_mobile = self._is_mobile_layout
        if mobile == previous_mobile:
            return

        if mobile:
            if not previous_mobile and self.analytics_toggle.isChecked():
                self._cached_splitter_sizes = self.splitter.sizes()
            if self.scroll_area.parent() is not self.mobile_container:
                self.scroll_area.setParent(self.mobile_container)
            if self.mobile_layout.indexOf(self.scroll_area) == -1:
                self.mobile_layout.insertWidget(0, self.scroll_area)
            if self.summary_frame.parent() is not self.mobile_container:
                self.summary_frame.setParent(self.mobile_container)
            if self.mobile_layout.indexOf(self.summary_frame) == -1:
                self.mobile_layout.addWidget(self.summary_frame)
            self.layout_stack.setCurrentWidget(self.mobile_container)
        else:
            if self.scroll_area.parent() is not self.splitter:
                self.scroll_area.setParent(self.splitter)
                self.splitter.insertWidget(0, self.scroll_area)
            elif self.splitter.indexOf(self.scroll_area) == -1:
                self.splitter.insertWidget(0, self.scroll_area)
            if self.summary_frame.parent() is not self.splitter:
                self.summary_frame.setParent(self.splitter)
            if self.splitter.indexOf(self.summary_frame) == -1:
                self.splitter.addWidget(self.summary_frame)
            if self.splitter.count() >= 2:
                self.splitter.setCollapsible(0, False)
                self.splitter.setCollapsible(1, True)
            self.layout_stack.setCurrentWidget(self.desktop_container)

        self._is_mobile_layout = mobile
        self._update_summary_visibility()

    def _update_summary_visibility(self) -> None:
        visible = self.analytics_toggle.isChecked()
        self.analytics_toggle.setText("Hide analytics" if visible else "Show analytics")
        if self._is_mobile_layout:
            self.summary_frame.setVisible(visible)
            return

        if self.splitter.count() < 2:
            return

        self._sync_analytics_cover_size()

        if visible:
            if self.summary_stack is not None and self.analytics_tabs is not None:
                self.summary_stack.setCurrentWidget(self.analytics_tabs)
            self.summary_frame.show()
            sizes = self._cached_splitter_sizes
            if not sizes or len(sizes) < 2 or sizes[1] == 0:
                total_width = max(self.width(), 600)
                left = max(int(total_width * 0.4), 320)
                right = max(total_width - left, 420)
                sizes = [left, right]
            self.splitter.setSizes(sizes)
            self._cached_splitter_sizes = sizes
        else:
            self._cached_splitter_sizes = self.splitter.sizes() if self.splitter.count() >= 2 else None
            if self.summary_stack is not None and self.analytics_cover is not None:
                self.summary_stack.setCurrentWidget(self.analytics_cover)
            self.summary_frame.show()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        width = event.size().width()
        use_mobile = width < 900
        self._apply_layout_mode(use_mobile)
        if not use_mobile and self.analytics_toggle.isChecked():
            total_width = max(width, 600)
            left = max(int(total_width * 0.4), 320)
            right = max(total_width - left, 420)
            sizes = [left, right]
            self.splitter.setSizes(sizes)
            self._cached_splitter_sizes = sizes
        self._sync_analytics_cover_size()

    def _sync_analytics_cover_size(self) -> None:
        if (
            self.summary_stack is None
            or self.analytics_tabs is None
            or self.analytics_cover is None
        ):
            return
        if self._is_mobile_layout:
            self.analytics_cover.setMinimumHeight(0)
            self.summary_stack.setMinimumHeight(0)
            return
        target_height = max(self.analytics_tabs.sizeHint().height(), self.summary_stack.minimumHeight())
        if target_height > 0:
            self.analytics_cover.setMinimumHeight(target_height)
            self.summary_stack.setMinimumHeight(target_height)
