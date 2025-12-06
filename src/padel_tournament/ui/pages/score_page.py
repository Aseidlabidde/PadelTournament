"""Schedule and score management page."""
from __future__ import annotations

from typing import Callable, Iterable, Mapping, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from ..loaders import load_ui
from .score_builder import ScorePageBuilder, ScorePageWidgets
from .score_components import AnalyticsSection, MatchesSection, RankingsSection

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
        matches_section: MatchesSection | None = None,
        rankings_section: RankingsSection | None = None,
        analytics_section: AnalyticsSection | None = None,
    ) -> None:
        super().__init__()
        load_ui(self, "pages/score_page/score_page.ui")

        self._on_score_changed = on_score_changed
        self._on_auto_toggle = on_auto_toggle
        self._cached_splitter_sizes: list[int] | None = None
        self._is_mobile_layout: bool = True
        builder = ScorePageBuilder(self)
        widgets, sections = builder.build(
            on_score_changed=self._on_score_changed,
            matches_section=matches_section,
            rankings_section=rankings_section,
            analytics_section=analytics_section,
        )

        self._apply_widgets(widgets)
        self._matches = sections.matches
        self._rankings = sections.rankings
        self._analytics = sections.analytics

        self.player_list.itemChanged.connect(self._handle_player_toggle)
        self.bar_player_list.itemChanged.connect(self._handle_bar_player_toggle)

        self.analytics_toggle.toggled.connect(self._toggle_analytics_panel)
        self.analytics_tabs.currentChanged.connect(self._handle_tab_changed)
        self.line_toggle.toggled.connect(self._handle_line_toggle)
        self.plot_graph_button.clicked.connect(self._handle_plot_graph_button)
        self.plot_bars_button.clicked.connect(self._handle_plot_bars_button)

        self.update_button.clicked.connect(on_update_rankings)
        self.save_button.clicked.connect(on_save)
        self.load_button.clicked.connect(on_load)
        self.csv_button.clicked.connect(on_export_csv)
        self.pdf_button.clicked.connect(on_export_pdf)
        self.back_button.clicked.connect(on_back)
        self.auto_checkbox.stateChanged.connect(self._handle_auto_toggled)

        self.analytics_toggle.setChecked(False)
        self.summary_stack.setCurrentWidget(self.analytics_cover)
        self.analytics_container.hide()

        self.set_auto_checked(True)
        self._apply_layout_mode(False)
        self._sync_analytics_cover_size()
        self._analytics.request_refresh("initial")

    def _apply_widgets(self, widgets: ScorePageWidgets) -> None:
        for name in widgets.__annotations__:
            setattr(self, name, getattr(widgets, name))


    # -- Match cards -----------------------------------------------------
    def populate_matches(self, matches: Sequence[Sequence[tuple[str, ...]]]) -> None:
        self._matches.populate(matches)

    def get_score_payload(self) -> list[dict[str, object]]:
        return self._matches.get_score_payload()

    def apply_score_payload(self, payload: Sequence[Mapping[str, object]]) -> None:
        self._matches.apply_score_payload(payload)

    def iter_scores(self) -> Iterable[tuple[tuple[str, ...], tuple[str, ...], str, str]]:
        return self._matches.iter_scores()

    # -- Rankings / Analytics --------------------------------------------
    def update_rankings_table(self, ranked: Sequence[tuple[int, str, int, int, int]]) -> None:
        self._rankings.update_rankings(ranked)

    def update_plot(self, history: Iterable[Mapping[str, int]], players: Iterable[str]) -> None:
        self._analytics.update_plot_data(history, players)

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
    # -- Plot filters -----------------------------------------------------
    def set_players_for_plot(self, players: Sequence[str]) -> None:
        self._analytics.set_players(players)

    def _handle_player_toggle(self, _item: object) -> None:
        self._analytics.handle_player_toggle()

    def _handle_bar_player_toggle(self, _item: object) -> None:
        self._analytics.handle_bar_player_toggle()

    def _handle_line_toggle(self, enabled: bool) -> None:
        self._analytics.handle_line_toggle(enabled)

    def apply_plot_theme(self, is_dark: bool) -> None:
        self._analytics.apply_theme(is_dark)

    def _handle_tab_changed(self, index: int) -> None:
        self._analytics.handle_tab_changed(index)

    def _handle_plot_graph_button(self) -> None:
        self._analytics.handle_plot_graph_button()

    def _handle_plot_bars_button(self) -> None:
        self._analytics.handle_plot_bars_button()

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
            if self.analytics_container.parent() is not self.mobile_container:
                self.analytics_container.setParent(self.mobile_container)
            if self.mobile_layout.indexOf(self.analytics_container) == -1:
                self.mobile_layout.addWidget(self.analytics_container)
            self.layout_stack.setCurrentWidget(self.mobile_container)
        else:
            if self.scroll_area.parent() is not self.splitter:
                self.scroll_area.setParent(self.splitter)
            if self.splitter.indexOf(self.scroll_area) == -1:
                self.splitter.insertWidget(0, self.scroll_area)
            if self.analytics_container.parent() is not self.splitter:
                self.analytics_container.setParent(self.splitter)
            container_index = self.splitter.indexOf(self.analytics_container)
            if container_index == -1:
                self.splitter.insertWidget(1, self.analytics_container)
                container_index = self.splitter.indexOf(self.analytics_container)
            if self.splitter.count() >= 2:
                self.splitter.setCollapsible(0, False)
                if container_index != -1:
                    self.splitter.setCollapsible(container_index, True)
            self.layout_stack.setCurrentWidget(self.desktop_container)

        self._is_mobile_layout = mobile
        self._update_summary_visibility()

    def _update_summary_visibility(self) -> None:
        visible = self.analytics_toggle.isChecked()
        self.analytics_toggle.setText("Hide analytics" if visible else "Show analytics")
        if self._is_mobile_layout:
            self.analytics_container.setVisible(visible)
            self.summary_frame.setVisible(visible)
            return

        if self.splitter.count() < 2:
            return

        self._sync_analytics_cover_size()

        if visible:
            if self.summary_stack is not None and self.analytics_page is not None:
                self.summary_stack.setCurrentWidget(self.analytics_page)
            self.analytics_container.show()
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
            self.analytics_container.hide()

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

