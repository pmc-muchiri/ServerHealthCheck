from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QRadioButton,
    QVBoxLayout,
)


class ReportSelectionDialog(QDialog):
    def __init__(self, server_labels: Iterable[str], current_label: str | None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Report Scope")
        self.resize(420, 380)

        layout = QVBoxLayout(self)
        intro = QLabel("Choose whether to export the current server, selected checked servers, or all checked servers.")
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.current_radio = QRadioButton("Current server")
        self.selected_radio = QRadioButton("Selected checked servers")
        self.all_radio = QRadioButton("All checked servers")
        self.current_radio.setChecked(True)

        self.mode_group = QButtonGroup(self)
        for button in (self.current_radio, self.selected_radio, self.all_radio):
            self.mode_group.addButton(button)
            layout.addWidget(button)

        self.current_radio.setEnabled(bool(current_label))
        if current_label:
            self.current_radio.setText(f"Current server: {current_label}")

        self.server_list = QListWidget()
        self.server_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        for label in server_labels:
            item = QListWidgetItem(label)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.server_list.addItem(item)
        layout.addWidget(self.server_list, 1)

        self.selected_radio.toggled.connect(self.server_list.setEnabled)
        self.server_list.setEnabled(False)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_mode(self) -> str:
        if self.all_radio.isChecked():
            return "all"
        if self.selected_radio.isChecked():
            return "selected"
        return "current"

    def selected_servers(self) -> list[str]:
        labels: list[str] = []
        for index in range(self.server_list.count()):
            item = self.server_list.item(index)
            if item.checkState() == Qt.CheckState.Checked:
                labels.append(item.text())
        return labels
