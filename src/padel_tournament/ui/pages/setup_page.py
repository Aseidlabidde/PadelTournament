"""Setup page for the tournament wizard."""
from __future__ import annotations

from typing import cast

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

from ..loaders import load_ui


class SetupPage(QWidget):
    """Initial page for configuring tournament basics."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self, "setup_page.ui")

        self.num_players_edit = cast(QLineEdit, self.findChild(QLineEdit, "num_players_edit"))
        self.team_size_edit = cast(QLineEdit, self.findChild(QLineEdit, "team_size_edit"))
        self.court_count_edit = cast(QLineEdit, self.findChild(QLineEdit, "court_count_edit"))
        self.next_button = cast(QPushButton, self.findChild(QPushButton, "next_button"))
        self.load_button = cast(QPushButton, self.findChild(QPushButton, "load_button"))
        self.example_button = cast(QPushButton, self.findChild(QPushButton, "example_button"))
        self.clear_button = cast(QPushButton, self.findChild(QPushButton, "clear_button"))

        # Apply styling hints that are easier to manage in code for now.
        title = cast(QLabel, self.findChild(QLabel, "title_label"))
        if title is not None:
            title.setObjectName("pageTitle")
            title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))

        for button in (self.load_button, self.example_button, self.clear_button):
            if button is not None:
                button.setObjectName("secondaryButton")

    def get_player_count_text(self) -> str:
        return self.num_players_edit.text().strip()

    def get_team_size_text(self) -> str:
        return self.team_size_edit.text().strip()

    def get_court_count_text(self) -> str:
        return self.court_count_edit.text().strip()

    def set_player_count(self, count: int) -> None:
        self.num_players_edit.setText(str(count))

    def set_team_size(self, size: int) -> None:
        self.team_size_edit.setText(str(size))

    def set_court_count(self, count: int) -> None:
        self.court_count_edit.setText(str(count))

    def clear_all(self) -> None:
        self.num_players_edit.clear()
        self.team_size_edit.clear()
        self.court_count_edit.clear()
        self.num_players_edit.setFocus()
