"""Player name entry page."""
from __future__ import annotations

from typing import Iterable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class NamesPage(QWidget):
    """Collects player names and forwards schedule generation requests."""

    def __init__(self) -> None:
        super().__init__()
        self._name_inputs: list[QLineEdit] = []
        self.generate_button = QPushButton("Generate Schedule")
        self.back_button = QPushButton("Back")

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        title = QLabel("Enter Player Names")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        layout.addWidget(title)

        self.names_container = QWidget()
        self.names_layout = QVBoxLayout(self.names_container)
        self.names_layout.setSpacing(8)
        self.names_layout.setContentsMargins(12, 12, 12, 12)

        self.names_scroll = QScrollArea()
        self.names_scroll.setWidgetResizable(True)
        self.names_scroll.setObjectName("namesScrollArea")
        self.names_scroll.setWidget(self.names_container)
        layout.addWidget(self.names_scroll)

        layout.addWidget(self.generate_button)

        back_layout = QHBoxLayout()
        self.back_button.setObjectName("secondaryButton")
        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)
        layout.addLayout(back_layout)

    def populate_inputs(self, count: int, preset_names: Iterable[str] | None = None) -> None:
        self.clear_inputs()
        preset_list = list(preset_names or [])
        for index in range(count):
            name_input = QLineEdit()
            name_input.setPlaceholderText(f"Player {index + 1}")
            if index < len(preset_list):
                name_input.setText(preset_list[index])
            self.names_layout.addWidget(name_input)
            self._name_inputs.append(name_input)
        self.names_layout.addStretch(1)

    def clear_inputs(self) -> None:
        while self.names_layout.count():
            item = self.names_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self._name_inputs = []

    def get_names(self) -> list[str]:
        return [line_edit.text().strip() for line_edit in self._name_inputs]
