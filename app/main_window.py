from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .app_logging import configure_logging, get_logger, log_path
from .inspector import build_metrics, build_requirements
from .layout_sections import build_footer, build_header, build_right_panel, build_sidebar, configure_file_menu
from .models import RequirementRow, Snapshot
from .pages import build_apps_page, build_dashboard_page, build_data_page, build_database_page, build_report_page
from .report_dialogs import ReportSelectionDialog
from .reporting import build_report_section, export_combined_report, export_report
from .theme import DARK_THEME, LIGHT_THEME
from .winrm import is_target_trusted
from .widgets import MetricCard
from .workers import InspectionThread


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.logger = get_logger()
        self.setWindowTitle("System Housekeeping")
        self.resize(1440, 920)

        self.dark_mode = True
        self.selected_target = ""
        self.snapshot = Snapshot()
        self.checked_snapshots: dict[str, Snapshot] = {}
        self.cpu_history: list[tuple[str, int]] = []
        self.worker: InspectionThread | None = None
        self.rerun_requested = False
        self.nav_buttons: list[QPushButton] = []

        self._build_ui()
        self._apply_theme()
        self._switch_page(0)
        self._populate_dashboard(self.snapshot)
        self._set_ready_state(True, "System ready. Press Run Check to start.")

    def _set_ready_state(self, ready: bool, message: str) -> None:
        self.apply_button.setEnabled(ready)
        self.target_input.setEnabled(ready)
        self.trusted_host_button.setEnabled(ready)
        self.run_button.setEnabled(ready)
        self.refresh_button.setEnabled(ready)
        self.target_status.setText(message)
        self.footer_activity.setText(message)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        shell = QHBoxLayout(central)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        self.sidebar = build_sidebar(self)
        shell.addWidget(self.sidebar)

        body = QFrame()
        body.setObjectName("centralBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        shell.addWidget(body, 1)

        body_layout.addWidget(build_header(self))

        content = QFrame()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        body_layout.addWidget(content, 1)

        self.pages = QStackedWidget()
        self.pages.addWidget(build_dashboard_page(self))
        self.pages.addWidget(build_data_page(self))
        self.pages.addWidget(build_database_page(self))
        self.pages.addWidget(build_apps_page(self))
        self.pages.addWidget(build_report_page(self))
        content_layout.addWidget(self.pages, 1)

        self.right_panel = build_right_panel(self)
        content_layout.addWidget(self.right_panel)

        body_layout.addWidget(build_footer(self))
        configure_file_menu(self)

    def _nav_button(self, text: str, index: int):
        from PySide6.QtWidgets import QPushButton

        button = QPushButton(text)
        button.setCheckable(True)
        button.clicked.connect(lambda checked=False, i=index: self._switch_page(i))
        self.nav_buttons.append(button)
        return button

    def _switch_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for idx, button in enumerate(self.nav_buttons):
            button.setChecked(idx == index)
            button.setProperty("activeNav", idx == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def _toggle_sidebar(self) -> None:
        expanded = self.sidebar.width() > 110
        self.sidebar.setFixedWidth(110 if expanded else 188)
        labels = ["Home", "System", "Database", "Apps", "Report"] if not expanded else ["H", "S", "DB", "A", "R"]
        for button, label in zip(self.nav_buttons, labels, strict=False):
            button.setText(label)

    def _apply_theme(self) -> None:
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_THEME if self.dark_mode else LIGHT_THEME)
        self.theme_button.setText("Light" if self.dark_mode else "Dark")

    def toggle_theme(self) -> None:
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def apply_target(self) -> None:
        self.selected_target = self.target_input.text().strip()
        self.logger.info("Apply target requested for target=%s", self.selected_target or "local machine")
        self.target_hint.setText(f"Current target: {self.selected_target or 'local machine'}")
        self.subtitle.setText(self.selected_target or "Local machine")
        self.check_trusted_host_status()
        self.target_status.setText("Target updated. Press Run Check when you're ready.")
        self.footer_activity.setText("Target updated")

    def check_trusted_host_status(self) -> None:
        target = self.target_input.text().strip() or self.selected_target
        if not target:
            self.trusted_host_status.setText("Enter a server name or IP first.")
            return
        try:
            trusted, entries = is_target_trusted(target)
        except Exception as error:  # noqa: BLE001
            self.logger.error("TrustedHosts status check failed for target=%s: %s", target, error)
            self.trusted_host_status.setText(f"TrustedHosts check failed: {error}")
            return

        if trusted:
            source = "*" if "*" in entries else target
            self.trusted_host_status.setText(f"TrustedHosts OK for {source}.")
        else:
            current_entries = ", ".join(entries) if entries else "(empty)"
            self.trusted_host_status.setText(
                f"{target} is not in TrustedHosts. Current list: {current_entries}"
            )

    def set_banner(self, message: str, stage: str, progress: int) -> None:
        self.banner_message.setText(message)
        self.banner_stage.setText(stage)
        self.banner_progress.setText(f"{progress}%")
        self.banner_bar.setValue(progress)
        self.footer_activity.setText(stage)

    def run_health_check(self) -> None:
        if self.worker and self.worker.isRunning():
            self.rerun_requested = True
            self.logger.info("Inspection request queued for target=%s", self.selected_target or "local machine")
            self.set_banner(
                f"Queued inspection for {self.selected_target or 'local machine'}.",
                "Waiting for current inspection to finish",
                10,
            )
            self.target_status.setText("A check is already running. Wait for the system to become ready.")
            return
        self.rerun_requested = False
        self.logger.info("Starting inspection for target=%s", self.selected_target or "local machine")
        self._set_ready_state(False, f"Checking {self.selected_target or 'local machine'}...")
        self.set_banner(f"Inspecting {self.selected_target or 'local machine'}...", "Collecting live machine snapshot", 20)
        self.worker = InspectionThread(self.selected_target)
        self.worker.completed.connect(self.handle_snapshot)
        self.worker.failed.connect(self.handle_error)
        self.worker.finished.connect(self.finish_run)
        self.worker.start()

    def finish_run(self) -> None:
        if not self.rerun_requested:
            self.logger.info("Inspection cycle finished and system is ready")
            self._set_ready_state(True, "System ready for a new server check.")
        if self.rerun_requested:
            self.logger.info("Running queued inspection next")
            self.target_status.setText("Starting queued server check...")
            QTimer.singleShot(0, self.run_health_check)

    def handle_snapshot(self, snapshot: Snapshot) -> None:
        self.logger.info("Snapshot received for computer=%s ip=%s", snapshot.computer_name, snapshot.primary_ip)
        self.snapshot = snapshot
        self.checked_snapshots[self._snapshot_label(snapshot)] = snapshot
        self.subtitle.setText(f"{snapshot.computer_name} · {snapshot.primary_ip}")
        self.last_checked.setText(f"Last checked: {snapshot.checked_at}")
        self.status_card.set_value("Live", "success")
        self.checked_card.set_value(snapshot.checked_at)
        self.uptime_card.set_value(snapshot.uptime_display)
        self.target_status.setText("System ready for a new server check.")
        self.set_banner(f"Live machine snapshot updated for {self.selected_target or snapshot.computer_name}.", "Live snapshot loaded", 100)
        self.quick_summary.setText(
            f"OS: {snapshot.os_caption}\n"
            f"CPU Cores: {snapshot.logical_cpu_count}\n"
            f"RAM: {snapshot.total_memory_gb:.1f} GB\n"
            f"CA GEN: {snapshot.ca_gen_version if snapshot.ca_gen_installed else 'Not detected'}"
        )
        self.report_summary.setText(
            f"Latest snapshot ready for export.\n"
            f"Checked at: {snapshot.checked_at}\n"
            f"Saved reports available for {len(self.checked_snapshots)} checked server(s)."
        )
        self._update_history(snapshot.cpu_percent)
        self._populate_dashboard(snapshot)

    def handle_error(self, error_message: str) -> None:
        self.logger.error("Inspection error shown in UI: %s", error_message)
        self.status_card.set_value("Inspection Failed", "danger")
        self.checked_card.set_value("Unavailable")
        self.uptime_card.set_value("Unavailable")
        self.target_status.setText("System ready. You can try another server.")
        self.set_banner(f"Inspection failed for {self.selected_target or 'local machine'}: {error_message}", "Inspection failed", 0)
        self.quick_summary.setText(error_message)
        self.report_summary.setText("No report available for the current target.")
        self._populate_dashboard(Snapshot())

    def _update_history(self, cpu_percent: float) -> None:
        label = datetime.now().strftime("%H:%M")
        self.cpu_history.append((label, int(round(cpu_percent))))
        self.cpu_history = self.cpu_history[-12:]
        self.chart.set_points(self.cpu_history)

    def _populate_dashboard(self, snapshot: Snapshot) -> None:
        metrics = build_metrics(snapshot)
        while self.metric_grid.count():
            item = self.metric_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        for index, metric in enumerate(metrics):
            card = MetricCard()
            card.set_metric(metric)
            row, column = divmod(index, 4)
            self.metric_grid.addWidget(card, row, column)

        self.services_table.set_rows(
            [[service.name, service.status, service.uptime] for service in snapshot.service_statuses]
            or [["No inspected services available.", "-", "-"]]
        )

        requirements: list[RequirementRow] = build_requirements(snapshot)
        self.requirements_table.set_rows([[row.component, row.required, row.actual, "PASS" if row.passed else "CHECK"] for row in requirements])

        self.database_table.set_rows(
            [[detail.label, detail.value] for detail in snapshot.database_details if detail.label != "Installed Software"]
            or [["No inspected database details available.", "Unavailable"]]
        )
        software_rows = [[software] for software in snapshot.installed_software] or [["No installed software inventory available."]]
        self.software_table.set_rows(software_rows)
        if self.software_table.columnCount() > 0:
            self.software_table.horizontalHeader().setStretchLastSection(True)

    def _snapshot_label(self, snapshot: Snapshot) -> str:
        server_name = snapshot.computer_name if snapshot.computer_name != "Unavailable" else self.selected_target or snapshot.primary_ip
        if snapshot.primary_ip and snapshot.primary_ip not in {"Unavailable", server_name}:
            return f"{server_name} ({snapshot.primary_ip})"
        return server_name

    def save_report(self) -> None:
        if not self.checked_snapshots and self.snapshot.computer_name == "Unavailable":
            QMessageBox.information(self, "No checked servers", "Run a server check first before generating reports.")
            return

        current_label = None if self.snapshot.computer_name == "Unavailable" else self._snapshot_label(self.snapshot)
        dialog = ReportSelectionDialog(self.checked_snapshots.keys(), current_label, self)
        if dialog.exec() == 0:
            return

        if dialog.selected_mode() == "current":
            snapshots = [self.snapshot] if current_label else []
        elif dialog.selected_mode() == "selected":
            selected_labels = dialog.selected_servers()
            if not selected_labels:
                QMessageBox.information(self, "No servers selected", "Select at least one checked server to generate a report.")
                return
            snapshots = [self.checked_snapshots[label] for label in selected_labels]
        else:
            snapshots = list(self.checked_snapshots.values())

        if not snapshots:
            QMessageBox.information(self, "No snapshots available", "There are no checked server snapshots available for export.")
            return

        selected_dir = QFileDialog.getExistingDirectory(self, "Choose report folder", str(Path.cwd()))
        if not selected_dir:
            return
        try:
            if len(snapshots) == 1:
                metrics = build_metrics(snapshots[0])
                requirements: list[RequirementRow] = build_requirements(snapshots[0])
                output_path = export_report(snapshots[0], metrics, requirements, Path(selected_dir))
            else:
                report_sections = [
                    build_report_section(server_snapshot, build_metrics(server_snapshot), build_requirements(server_snapshot))
                    for server_snapshot in snapshots
                ]
                output_path = export_combined_report(report_sections, Path(selected_dir))
        except Exception as error:  # noqa: BLE001
            QMessageBox.critical(self, "Report export failed", str(error))
            return
        self.set_banner(f"Report exported to {output_path}.", "Report ready", 100)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_path)))


def run() -> None:
    configure_logging()
    app = QApplication(sys.argv)
    get_logger().info("Application started. Log file: %s", log_path())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
