"""Player name entry page."""
from __future__ import annotations

from typing import Iterable, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget

from ..loaders import load_ui


class NamesPage(QWidget):
    """Collects player names and forwards schedule generation requests."""

    def __init__(self) -> None:
        super().__init__()
        load_ui(self, "pages/names_page/names_page.ui")

        self._name_inputs: list[QLineEdit] = []
        self.generate_button = cast(QPushButton, self.findChild(QPushButton, "generate_button"))
        self.back_button = cast(QPushButton, self.findChild(QPushButton, "back_button"))
        self.fill_button = cast(QPushButton, self.findChild(QPushButton, "fill_button"))
        self.names_scroll = cast(QScrollArea, self.findChild(QScrollArea, "names_scroll"))
        self.names_container = cast(QWidget, self.findChild(QWidget, "names_container"))
        self.names_layout = cast(QVBoxLayout, self.findChild(QVBoxLayout, "names_layout"))
        self.main_layout = cast(QVBoxLayout, self.findChild(QVBoxLayout, "mainLayout"))
        self.button_layout = cast(QHBoxLayout, self.findChild(QHBoxLayout, "buttonLayout"))

        if self.names_layout is not None:
            self.names_layout.setContentsMargins(12, 12, 12, 12)
            self.names_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title = cast(QLabel, self.findChild(QLabel, "title_label"))
        if title is not None:
            title.setObjectName("pageTitle")

        if self.back_button is not None:
            self.back_button.setObjectName("secondaryButton")
        if self.main_layout is not None and self.button_layout is not None:
            self.main_layout.setAlignment(self.button_layout, Qt.AlignmentFlag.AlignHCenter)
        if self.fill_button is not None:
            self.fill_button.setObjectName("secondaryButton")
            self.fill_button.clicked.connect(self._fill_with_generic_names)

    def populate_inputs(self, count: int, preset_names: Iterable[str] | None = None) -> None:
        self.clear_inputs()
        preset_list = list(preset_names or [])
        for index in range(count):
            name_input = QLineEdit()
            name_input.setPlaceholderText(f"Player {index + 1}")
            name_input.setMaximumWidth(320)
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

    def _fill_with_generic_names(self) -> None:
        if not self._name_inputs:
            return
        for index, line_edit in enumerate(self._name_inputs, start=1):
            line_edit.setText(f"Player {index}")
