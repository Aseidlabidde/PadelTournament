"""Setup page for the tournament wizard."""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SetupPage(QWidget):
    """Initial page for configuring tournament basics."""

    def __init__(self) -> None:
        super().__init__()
        self.num_players_edit = QLineEdit()
        self.team_size_edit = QLineEdit()
        self.court_count_edit = QLineEdit()
        self.next_button = QPushButton("Next — Enter Names")
        self.load_button = QPushButton("Load Tournament")
        self.example_button = QPushButton("Load Example")
        self.clear_button = QPushButton("Reset")

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Tournament Setup")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.num_players_edit.setPlaceholderText("e.g. 8")
        form.addRow("Number of players:", self.num_players_edit)

        self.team_size_edit.setPlaceholderText("e.g. 2")
        self.team_size_edit.setText("2")
        form.addRow("Team size (x for x-vs-x):", self.team_size_edit)

        self.court_count_edit.setPlaceholderText("e.g. 1")
        self.court_count_edit.setText("1")
        form.addRow("Number of courts:", self.court_count_edit)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(self.next_button)

        self.load_button.setObjectName("secondaryButton")
        buttons.addWidget(self.load_button)

        self.example_button.setObjectName("secondaryButton")
        buttons.addWidget(self.example_button)

        self.clear_button.setObjectName("secondaryButton")
        buttons.addWidget(self.clear_button)

        layout.addLayout(buttons)
        layout.addStretch(1)

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
