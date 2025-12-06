"""Setup page for the tournament wizard."""
from __future__ import annotations

from typing import cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from ..loaders import load_ui


class SetupPage(QWidget):
    """Initial page for configuring tournament basics."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self, "pages/setup_page/setup_page.ui")

        self.num_players_edit = cast(QLineEdit, self.findChild(QLineEdit, "num_players_edit"))
        self.team_size_edit = cast(QLineEdit, self.findChild(QLineEdit, "team_size_edit"))
        self.court_count_edit = cast(QLineEdit, self.findChild(QLineEdit, "court_count_edit"))
        self.next_button = cast(QPushButton, self.findChild(QPushButton, "next_button"))
        self.load_button = cast(QPushButton, self.findChild(QPushButton, "load_button"))
        self.clear_button = cast(QPushButton, self.findChild(QPushButton, "clear_button"))
        self.main_layout = cast(QVBoxLayout, self.findChild(QVBoxLayout, "mainLayout"))
        self.form_container = cast(QHBoxLayout, self.findChild(QHBoxLayout, "formContainer"))
        self.form_layout = cast(QFormLayout, self.findChild(QFormLayout, "formLayout"))
        self.button_layout = cast(QHBoxLayout, self.findChild(QHBoxLayout, "buttonLayout"))

        # Apply styling hints that are easier to manage in code for now.
        title = cast(QLabel, self.findChild(QLabel, "title_label"))
        if title is not None:
            title.setObjectName("pageTitle")

        for button in (self.load_button, self.clear_button):
            if button is not None:
                button.setObjectName("secondaryButton")

        if self.button_layout is not None:
            self.button_layout.setSpacing(4)

        if self.main_layout is not None and self.form_container is not None:
            self.main_layout.setAlignment(self.form_container, Qt.AlignmentFlag.AlignHCenter)
        if self.main_layout is not None and self.button_layout is not None:
            self.main_layout.setAlignment(self.button_layout, Qt.AlignmentFlag.AlignHCenter)

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
