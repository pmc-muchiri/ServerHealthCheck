from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .widgets import DataTable, KpiCard, LineChartWidget, Panel, RequirementsTable, ServicesTable


def build_dashboard_page(window) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(16)

    kpi_row = QHBoxLayout()
    kpi_row.setSpacing(16)
    window.status_card = KpiCard("Server Status", "Live", "success")
    window.checked_card = KpiCard("Last Checked", "Unavailable")
    window.uptime_card = KpiCard("Uptime", "Unavailable")
    window.auto_card = KpiCard("Auto Refresh", "15s")
    for card in (window.status_card, window.checked_card, window.uptime_card, window.auto_card):
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        kpi_row.addWidget(card)
    layout.addLayout(kpi_row)

    section = QLabel("Resource Utilization")
    section.setProperty("section", True)
    layout.addWidget(section)

    window.metric_grid_holder = QWidget()
    window.metric_grid = QGridLayout(window.metric_grid_holder)
    window.metric_grid.setSpacing(14)
    layout.addWidget(window.metric_grid_holder)

    lower = QHBoxLayout()
    lower.setSpacing(16)
    cpu_panel = Panel("CPU Usage (24H)")
    window.chart = LineChartWidget()
    cpu_panel.body.addWidget(window.chart)
    lower.addWidget(cpu_panel, 3)

    services_panel = Panel("Services")
    window.services_table = ServicesTable(["Service", "Status", "Uptime"])
    services_panel.body.addWidget(window.services_table)
    lower.addWidget(services_panel, 2)
    layout.addLayout(lower)
    return page


def build_data_page(window) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(16)

    requirements_panel = Panel("System Requirements Check")
    window.requirements_table = RequirementsTable(["Component", "Required", "Actual", "Status"])
    requirements_panel.body.addWidget(window.requirements_table)
    layout.addWidget(requirements_panel)
    return page


def build_report_page(window) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(16)

    panel = Panel("Report Center")
    intro = QLabel("Generate a downloadable HTML report from the latest inspected snapshot.")
    intro.setWordWrap(True)
    intro.setProperty("muted", True)
    window.report_summary = QLabel("No report generated yet.")
    window.report_summary.setWordWrap(True)

    export_button = QPushButton("Export Current Report")
    export_button.setProperty("primary", True)
    export_button.clicked.connect(window.save_report)

    panel.body.addWidget(intro)
    panel.body.addWidget(window.report_summary)
    panel.body.addWidget(export_button, alignment=Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(panel)
    return page


def build_database_page(window) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(16)

    database_panel = Panel("Database Information")
    window.database_table = DataTable(["Property", "Value"])
    database_panel.body.addWidget(window.database_table)
    layout.addWidget(database_panel)
    return page


def build_apps_page(window) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(16)

    software_panel = Panel("Installed Software")
    window.software_table = DataTable(["Software"])
    software_panel.body.addWidget(window.software_table)
    layout.addWidget(software_panel)
    return page
