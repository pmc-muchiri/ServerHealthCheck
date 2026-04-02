from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from .widgets import Panel


def build_sidebar(window) -> QFrame:
    sidebar = QFrame()
    sidebar.setObjectName("leftMenuSubContainer")
    sidebar.setFixedWidth(96)

    sidebar_layout = QVBoxLayout(sidebar)
    sidebar_layout.setContentsMargins(10, 10, 10, 10)
    sidebar_layout.setSpacing(10)

    window.menu_toggle = QPushButton("|||")
    window.menu_toggle.clicked.connect(window._toggle_sidebar)
    window.menu_toggle.setObjectName("menuButton")
    sidebar_layout.addWidget(window.menu_toggle)

    window.home_btn = window._nav_button("Home", 0)
    window.data_btn = window._nav_button("Data", 1)
    window.database_btn = window._nav_button("Database", 2)
    window.apps_btn = window._nav_button("Apps", 3)
    window.report_btn = window._nav_button("Report", 4)
    for button in (window.home_btn, window.data_btn, window.database_btn, window.apps_btn, window.report_btn):
        sidebar_layout.addWidget(button)
    sidebar_layout.addStretch(1)

    window.theme_side_btn = QPushButton("Theme")
    window.theme_side_btn.clicked.connect(window.toggle_theme)
    sidebar_layout.addWidget(window.theme_side_btn)
    return sidebar


def build_header(window) -> QFrame:
    header = QFrame()
    header.setObjectName("headerContainer")
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(16, 12, 16, 12)
    header_layout.setSpacing(16)

    brand_wrap = QHBoxLayout()
    window.logo_badge = QLabel("22")
    window.logo_badge.setObjectName("logoBadge")
    window.logo_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
    brand_wrap.addWidget(window.logo_badge)

    brand_text = QVBoxLayout()
    window.title_label = QLabel("System Housekeeping")
    window.title_label.setProperty("title", True)
    window.subtitle = QLabel("Local machine")
    window.subtitle.setProperty("subtitle", True)
    brand_text.addWidget(window.title_label)
    brand_text.addWidget(window.subtitle)
    brand_wrap.addLayout(brand_text)
    header_layout.addLayout(brand_wrap)
    header_layout.addStretch(1)

    window.last_checked = QLabel("Last checked: Unavailable")
    window.last_checked.setProperty("muted", True)
    header_layout.addWidget(window.last_checked)

    window.theme_button = QPushButton("Day")
    window.theme_button.clicked.connect(window.toggle_theme)
    header_layout.addWidget(window.theme_button)

    window.report_button = QPushButton("Report")
    window.report_button.clicked.connect(window.save_report)
    header_layout.addWidget(window.report_button)

    window.run_button = QPushButton("Run Check")
    window.run_button.setProperty("primary", True)
    window.run_button.clicked.connect(window.run_health_check)
    header_layout.addWidget(window.run_button)

    window.refresh_button = QPushButton("Refresh")
    window.refresh_button.clicked.connect(window.run_health_check)
    header_layout.addWidget(window.refresh_button)
    return header


def build_right_panel(window) -> QFrame:
    right_panel = QFrame()
    right_panel.setObjectName("rightMenuSubContainer")
    right_panel.setFixedWidth(270)

    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(14, 14, 14, 14)
    right_layout.setSpacing(12)

    target_panel = Panel("Inspection Target")
    target_label = QLabel("Server Name or IP")
    target_label.setProperty("muted", True)
    window.target_input = QLineEdit()
    window.target_input.setPlaceholderText("10.0.1.42 or PROD-SQL-01")
    window.apply_button = QPushButton("Apply Target")
    window.apply_button.setProperty("primary", True)
    window.apply_button.clicked.connect(window.apply_target)
    window.target_hint = QLabel("Current target: local machine")
    window.target_hint.setProperty("muted", True)
    window.trusted_host_button = QPushButton("Check Trusted Host")
    window.trusted_host_button.clicked.connect(window.check_trusted_host_status)
    window.trusted_host_status = QLabel("TrustedHosts status not checked yet.")
    window.trusted_host_status.setProperty("muted", True)
    window.target_status = QLabel("System ready for a new server check.")
    window.target_status.setProperty("muted", True)
    target_panel.body.addWidget(target_label)
    target_panel.body.addWidget(window.target_input)
    target_panel.body.addWidget(window.apply_button, alignment=Qt.AlignmentFlag.AlignLeft)
    target_panel.body.addWidget(window.target_hint)
    target_panel.body.addWidget(window.trusted_host_button, alignment=Qt.AlignmentFlag.AlignLeft)
    target_panel.body.addWidget(window.trusted_host_status)
    target_panel.body.addWidget(window.target_status)
    right_layout.addWidget(target_panel)

    activity_panel = Panel("Activity")
    window.banner_message = QLabel("Desktop dashboard ready. Run a health check to inspect a machine.")
    window.banner_message.setWordWrap(True)
    window.banner_stage = QLabel("Ready")
    window.banner_stage.setProperty("muted", True)
    window.banner_bar = QProgressBar()
    window.banner_bar.setTextVisible(False)
    window.banner_bar.setValue(0)
    window.banner_progress = QLabel("0%")
    window.banner_progress.setProperty("mono", True)
    activity_panel.body.addWidget(window.banner_message)
    activity_panel.body.addWidget(window.banner_stage)
    activity_panel.body.addWidget(window.banner_bar)
    activity_panel.body.addWidget(window.banner_progress, alignment=Qt.AlignmentFlag.AlignRight)
    right_layout.addWidget(activity_panel)

    quick_panel = Panel("Quick View")
    window.quick_summary = QLabel("Status and machine details will appear here after inspection.")
    window.quick_summary.setWordWrap(True)
    window.quick_summary.setProperty("muted", True)
    quick_panel.body.addWidget(window.quick_summary)
    right_layout.addWidget(quick_panel)
    right_layout.addStretch(1)
    return right_panel


def build_footer(window) -> QFrame:
    footer = QFrame()
    footer.setObjectName("footerContainter")
    footer_layout = QHBoxLayout(footer)
    footer_layout.setContentsMargins(16, 8, 16, 8)
    footer_layout.setSpacing(12)

    window.footer_label = QLabel("Housekeeping Desktop")
    window.footer_label.setProperty("muted", True)
    footer_layout.addWidget(window.footer_label)
    footer_layout.addStretch(1)

    window.footer_activity = QLabel("Idle")
    window.footer_activity.setProperty("muted", True)
    footer_layout.addWidget(window.footer_activity)
    return footer


def configure_file_menu(window: QMainWindow) -> None:
    file_menu = window.menuBar().addMenu("File")
    export_action = QAction("Export Report", window)
    export_action.triggered.connect(window.save_report)
    file_menu.addAction(export_action)
