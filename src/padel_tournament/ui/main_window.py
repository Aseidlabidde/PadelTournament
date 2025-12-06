"""Main window composition and application orchestration."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence, cast

from PyQt6.QtCore import QByteArray, QSettings, Qt, QTimer
from PyQt6.QtGui import QAction, QCloseEvent, QFont
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout

from ..core import TournamentState, generate_schedule
from ..services import RankingResult, compute_rankings
from ..services.persistence import export_csv, export_pdf, load_payload, save_payload
from ..themes import DARK_THEME, LIGHT_THEME, load_stylesheet
from .loaders import load_ui
from .pages import NamesPage, ScorePage, SetupPage

ScoreTuple = tuple[tuple[str, ...], tuple[str, ...], str, str]


class TournamentApp(QMainWindow):
    """Main window composed of three stacked pages."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self, "pages/main_window/main_window.ui")
        self.setMinimumSize(980, 720)

        central_layout = cast(QVBoxLayout, self.findChild(QVBoxLayout, "centralLayout"))
        if central_layout is not None:
            central_layout.setContentsMargins(0, 0, 0, 0)

        self.settings = QSettings("PadelTournament", "Manager")
        self.current_theme = LIGHT_THEME
        self._last_file_path: str | None = None
        self._pending_recent_file: str | None = None

        self.state = TournamentState()
        self._ranking_snapshot: list[tuple[int, str, int, int, int]] = []
        self._latest_scores: list[ScoreTuple] = []
        self.auto_timer = QTimer(self)
        self.auto_timer.setSingleShot(True)
        self.auto_timer.setInterval(300)
        self.auto_timer.timeout.connect(self.update_rankings)

        self.stack = cast(QStackedWidget, self.findChild(QStackedWidget, "stack"))
        if self.stack is None:
            raise RuntimeError("Main window UI is missing the central 'stack' widget")

        self.save_action = cast(QAction, self.findChild(QAction, "save_action"))
        self.load_action = cast(QAction, self.findChild(QAction, "load_action"))
        self.csv_action = cast(QAction, self.findChild(QAction, "csv_action"))
        self.pdf_action = cast(QAction, self.findChild(QAction, "pdf_action"))
        self.exit_action = cast(QAction, self.findChild(QAction, "exit_action"))
        self.theme_action = cast(QAction, self.findChild(QAction, "theme_action"))
        self.auto_action = cast(QAction, self.findChild(QAction, "auto_action"))

        self.setup_page = SetupPage()
        self.names_page = NamesPage()
        self.score_page = ScorePage(
            on_score_changed=self._on_score_changed,
            on_update_rankings=self.update_rankings,
            on_save=self.save_tournament,
            on_load=self.load_tournament,
            on_export_csv=self.export_csv,
            on_export_pdf=self.export_pdf,
            on_back=self._navigate_to_setup,
            on_auto_toggle=self._handle_auto_toggle,
        )

        self._wire_actions()
        self._connect_page_events()

        self.stack.addWidget(self.setup_page)
        self.stack.addWidget(self.names_page)
        self.stack.addWidget(self.score_page)
        self.stack.setCurrentWidget(self.setup_page)
        self._restore_settings()
        self._load_recent_file()

    # -- Menu ------------------------------------------------------------
    def _wire_actions(self) -> None:
        self.save_action.triggered.connect(self.save_tournament)
        self.load_action.triggered.connect(self.load_tournament)
        self.csv_action.triggered.connect(self.export_csv)
        self.pdf_action.triggered.connect(self.export_pdf)
        self.exit_action.triggered.connect(self.close)

        self.theme_action.triggered.connect(self.toggle_theme)
        self.auto_action.triggered.connect(lambda: self._handle_auto_toggle(self.auto_action.isChecked()))
        self.auto_action.setChecked(True)

    def _connect_page_events(self) -> None:
        self.setup_page.next_button.clicked.connect(self._handle_setup_next)
        self.setup_page.load_button.clicked.connect(self.load_tournament)
        self.setup_page.clear_button.clicked.connect(self._clear_setup)

        self.names_page.generate_button.clicked.connect(self._handle_generate_schedule)
        self.names_page.back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.setup_page))

    # -- Navigation ------------------------------------------------------
    def _navigate_to_setup(self) -> None:
        self.stack.setCurrentWidget(self.setup_page)

    def _navigate_to_names(self) -> None:
        self.stack.setCurrentWidget(self.names_page)

    def _navigate_to_scores(self) -> None:
        self.stack.setCurrentWidget(self.score_page)

    # -- Page handlers ---------------------------------------------------
    def _handle_setup_next(self) -> None:
        try:
            player_count = int(self.setup_page.get_player_count_text())
        except ValueError:
            self._show_error("Please enter a valid number of players.")
            return

        if player_count < 2:
            self._show_error("Need at least 2 players.")
            return

        try:
            team_size = int(self.setup_page.get_team_size_text())
            court_count = int(self.setup_page.get_court_count_text())
        except ValueError:
            self._show_error("Team size and courts must be integers.")
            return

        self.state.team_size = team_size
        self.state.num_courts = court_count

        preset_names = self.state.names if len(self.state.names) == player_count else []
        self.names_page.populate_inputs(player_count, preset_names)
        self._navigate_to_names()

    def _handle_generate_schedule(self) -> None:
        names = self.names_page.get_names()
        if any(not name for name in names):
            self._show_error("Names must be non-empty.")
            return
        if len(set(names)) != len(names):
            self._show_error("Names must be unique.")
            return

        self.state.names = names
        try:
            team_size = int(self.setup_page.get_team_size_text())
            court_count = int(self.setup_page.get_court_count_text())
        except ValueError:
            self._show_error("Team size and courts must be integers.")
            return

        if team_size < 2 or court_count < 1:
            self._show_error("Team size must be ≥ 2 and courts ≥ 1.")
            return

        schedule = generate_schedule(names, team_size, court_count)
        if not schedule:
            self._show_error("Failed to generate schedule with these parameters.")
            return

        self.state.team_size = team_size
        self.state.num_courts = court_count
        self.state.matches = schedule
        self.state.history.clear()

        self.score_page.populate_matches(schedule)
        self.score_page.set_players_for_plot(self.state.names)
        self._navigate_to_scores()
        self.update_rankings()

    # -- Score updates ---------------------------------------------------
    def _on_score_changed(self) -> None:
        if self.auto_action.isChecked():
            self.auto_timer.start()

    def _handle_auto_toggle(self, enabled: bool) -> None:
        if self.auto_action.isChecked() != enabled:
            self.auto_action.blockSignals(True)
            self.auto_action.setChecked(enabled)
            self.auto_action.blockSignals(False)
        if self.score_page.is_auto_enabled() != enabled:
            self.score_page.set_auto_checked(enabled)
        if not enabled:
            self.auto_timer.stop()

    def is_auto_enabled(self) -> bool:
        return self.auto_action.isChecked()

    def update_rankings(self) -> None:
        if not self.state.matches:
            self.score_page.update_rankings_table([])
            self.score_page.update_plot([], [])
            self._ranking_snapshot = []
            self._latest_scores = []
            return

        scores = list(self.score_page.iter_scores())
        result: RankingResult = compute_rankings(self.state.matches, self.state.names, scores)
        self.state.history = result.history
        self._ranking_snapshot = result.rankings
        self._latest_scores = scores

        self.score_page.update_rankings_table(result.rankings)
        self.score_page.update_plot(result.history, self.state.names)

    # -- Persistence -----------------------------------------------------
    def save_tournament(self) -> None:
        if not self.state.matches:
            QMessageBox.information(self, "Nothing to save", "No tournament to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save tournament", filter="JSON files (*.json)")
        if not file_path:
            return

        try:
            save_payload(file_path, self.state, self.score_page.get_score_payload())
        except OSError as exc:
            self._show_error(f"Failed to save: {exc}")
            return

        self._remember_last_file(file_path)
        QMessageBox.information(self, "Saved", f"Saved to {file_path}")

    def load_tournament(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Load tournament", filter="JSON files (*.json)")
        if not file_path:
            return
        self._perform_load(file_path)

    # -- Export ----------------------------------------------------------
    def export_csv(self) -> None:
        if not self.state.matches:
            QMessageBox.information(self, "Nothing to export", "No tournament data.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export CSV", filter="CSV files (*.csv)")
        if not file_path:
            return

        self.update_rankings()
        try:
            export_csv(file_path, self.state.matches, self._ranking_snapshot, self._latest_scores)
        except OSError as exc:
            self._show_error(f"CSV export failed: {exc}")
            return

        QMessageBox.information(self, "Exported", f"CSV saved to {file_path}")

    def export_pdf(self) -> None:
        if not self.state.matches:
            QMessageBox.information(self, "Nothing to export", "No tournament data.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", filter="PDF files (*.pdf)")
        if not file_path:
            return

        self.update_rankings()
        try:
            export_pdf(file_path, self.state, self._ranking_snapshot, self._latest_scores)
        except Exception as exc:  # noqa: BLE001
            self._show_error(f"PDF export failed: {exc}")
            return

        QMessageBox.information(self, "Exported", f"PDF saved to {file_path}")

    # -- Themes ----------------------------------------------------------
    def toggle_theme(self) -> None:
        theme = DARK_THEME if self.theme_action.isChecked() else LIGHT_THEME
        self.apply_theme(theme)

    def apply_theme(self, theme_name: str) -> None:
        stylesheet = load_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        is_dark = theme_name == DARK_THEME
        self.theme_action.blockSignals(True)
        self.theme_action.setChecked(is_dark)
        self.theme_action.blockSignals(False)
        self.current_theme = theme_name
        self.score_page.apply_plot_theme(is_dark)

    # -- Helpers ---------------------------------------------------------
    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    def _perform_load(self, file_path: str, *, show_message: bool = True, notify_missing: bool = True) -> None:
        path = Path(file_path)
        if notify_missing and not path.exists():
            self._show_error(f"File not found: {file_path}")
            return

        try:
            state, scores = load_payload(path)
        except Exception as exc:  # noqa: BLE001
            if notify_missing:
                self._show_error(f"Failed to read file: {exc}")
            return

        self.state = state
        player_count = len(self.state.names)
        self.setup_page.set_player_count(player_count)
        self.setup_page.set_team_size(self.state.team_size)
        self.setup_page.set_court_count(self.state.num_courts)
        self.names_page.populate_inputs(player_count, self.state.names)

        self.score_page.populate_matches(self.state.matches)
        self.score_page.apply_score_payload(scores)
        self.score_page.set_players_for_plot(self.state.names)
        self._navigate_to_scores()
        self.update_rankings()
        self._remember_last_file(str(path))
        if show_message:
            QMessageBox.information(self, "Loaded", f"Loaded from {file_path}")

    def _remember_last_file(self, file_path: str) -> None:
        self._last_file_path = file_path
        self.settings.setValue("recent/file", file_path)

    def _restore_settings(self) -> None:
        geometry = self.settings.value("window/geometry")
        if isinstance(geometry, QByteArray) and not geometry.isEmpty():
            self.restoreGeometry(geometry)

        window_state = self.settings.value("window/state")
        if isinstance(window_state, QByteArray) and not window_state.isEmpty():
            self.restoreState(window_state)

        theme = self.settings.value("preferences/theme", LIGHT_THEME)
        if not isinstance(theme, str) or theme not in {LIGHT_THEME, DARK_THEME}:
            theme = LIGHT_THEME
        self.apply_theme(theme)

        auto_enabled = self.settings.value("preferences/auto_update", True, type=bool)
        self._handle_auto_toggle(bool(auto_enabled))

        recent = self.settings.value("recent/file")
        if isinstance(recent, str) and recent:
            self._last_file_path = recent
            if Path(recent).exists():
                self._pending_recent_file = recent

    def _load_recent_file(self) -> None:
        if not self._pending_recent_file:
            return
        recent = self._pending_recent_file
        self._pending_recent_file = None
        self._perform_load(recent, show_message=False, notify_missing=False)

    def _clear_setup(self) -> None:
        self.setup_page.clear_all()
        self.names_page.clear_inputs()
        self.state = TournamentState()
        self._ranking_snapshot = []
        self._latest_scores = []
        self.score_page.populate_matches([])
        self.score_page.update_rankings_table([])
        self.score_page.set_players_for_plot([])

    def _save_settings(self) -> None:
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/state", self.saveState())
        self.settings.setValue("preferences/theme", self.current_theme)
        self.settings.setValue("preferences/auto_update", self.auto_action.isChecked())
        if self._last_file_path:
            self.settings.setValue("recent/file", self._last_file_path)
        else:
            self.settings.remove("recent/file")

    def closeEvent(self, event: QCloseEvent) -> None:
        self._save_settings()
        super().closeEvent(event)


def create_application() -> QApplication:
    """Create the QApplication instance with sensible defaults."""

    use_high_dpi = getattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps", None)
    if use_high_dpi is not None:
        QApplication.setAttribute(use_high_dpi, True)
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    return app


def launch() -> None:
    """Launch the tournament manager UI."""

    app = create_application()
    window = TournamentApp()
    window.show()
    sys.exit(app.exec())
