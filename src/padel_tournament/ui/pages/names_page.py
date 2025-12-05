"""Player name entry page."""
from __future__ import annotations

from typing import Iterable, cast

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from ..loaders import load_ui


class NamesPage(QWidget):
    """Collects player names and forwards schedule generation requests."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self, "names_page.ui")

        self._name_inputs: list[QLineEdit] = []
        self.generate_button = cast(QPushButton, self.findChild(QPushButton, "generate_button"))
        self.back_button = cast(QPushButton, self.findChild(QPushButton, "back_button"))
        self.names_scroll = cast(QScrollArea, self.findChild(QScrollArea, "names_scroll"))
        self.names_container = cast(QWidget, self.findChild(QWidget, "names_container"))
        self.names_layout = cast(QVBoxLayout, self.findChild(QVBoxLayout, "names_layout"))

        title = cast(QLabel, self.findChild(QLabel, "title_label"))
        if title is not None:
            title.setObjectName("pageTitle")
            title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))

        if self.back_button is not None:
            self.back_button.setObjectName("secondaryButton")

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
