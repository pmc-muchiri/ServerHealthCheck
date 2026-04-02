from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .models import Metric


class Panel(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("panel", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(12)
        self.title_label = QLabel(title)
        self.title_label.setProperty("panelTitle", True)
        layout.addWidget(self.title_label)
        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(10)
        layout.addLayout(self.body)


class KpiCard(QFrame):
    def __init__(self, label: str, value: str, accent: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("kpi", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        self.label = QLabel(label)
        self.label.setProperty("muted", True)
        self.value = QLabel(value)
        if accent:
            self.value.setProperty(accent, True)
        self.value.setWordWrap(True)
        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, text: str, accent: str | None = None) -> None:
        self.value.setText(text)
        for name in ("success", "warn", "danger"):
            self.value.setProperty(name, False)
        if accent:
            self.value.setProperty(accent, True)
        self.style().unpolish(self.value)
        self.style().polish(self.value)


class MetricCard(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("metric", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        self.label = QLabel("")
        self.label.setProperty("section", True)
        self.value = QLabel("")
        self.value.setStyleSheet("font-size: 16pt; font-weight: 700;")
        header.addWidget(self.label)
        header.addStretch(1)
        header.addWidget(self.value)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.meta = QHBoxLayout()
        self.min_label = QLabel("")
        self.min_label.setProperty("muted", True)
        self.max_label = QLabel("")
        self.max_label.setProperty("muted", True)
        self.meta.addWidget(self.min_label)
        self.meta.addStretch(1)
        self.meta.addWidget(self.max_label)

        layout.addLayout(header)
        layout.addWidget(self.progress)
        layout.addLayout(self.meta)

    def set_metric(self, metric: Metric) -> None:
        self.label.setText(metric.label)
        self.value.setText(metric.display_value)
        self.progress.setValue(metric.progress)
        self.min_label.setText(metric.min_label)
        self.max_label.setText(metric.max_label)


class LineChartWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.points: list[tuple[str, int]] = []
        self.setMinimumHeight(240)

    def set_points(self, points: list[tuple[str, int]]) -> None:
        self.points = points[-12:]
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(18, 12, -18, -26)

        safe_points = self.points if len(self.points) >= 2 else [("00:00", 0), ("01:00", 0)]
        grid_pen = QPen(QColor("#d8e1ec"))
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        line_pen = QPen(QColor("#3167e3"), 3)
        area_color = QColor("#3167e3")
        area_color.setAlpha(28)

        for tick in range(0, 101, 25):
            y = rect.bottom() - (tick / 100.0) * rect.height()
            painter.setPen(grid_pen)
            painter.drawLine(rect.left(), y, rect.right(), y)
            painter.setPen(QColor("#64748b"))
            painter.drawText(0, int(y) + 4, 36, 16, Qt.AlignmentFlag.AlignRight, f"{tick}%")

        step = rect.width() / max(1, len(safe_points) - 1)
        chart_points: list[QPointF] = []
        for index, (label, value) in enumerate(safe_points):
            x = rect.left() + index * step
            y = rect.bottom() - (max(0, min(100, value)) / 100.0) * rect.height()
            chart_points.append(QPointF(x, y))
            painter.setPen(QColor("#64748b"))
            painter.drawText(int(x) - 18, rect.bottom() + 8, 40, 18, Qt.AlignmentFlag.AlignHCenter, label)

        line_path = self._smooth_path(chart_points)
        area_path = QPainterPath(line_path)
        area_path.lineTo(QPointF(chart_points[-1].x(), rect.bottom()))
        area_path.lineTo(QPointF(chart_points[0].x(), rect.bottom()))
        area_path.closeSubpath()

        painter.fillPath(area_path, area_color)
        painter.setPen(line_pen)
        painter.drawPath(line_path)

    def _smooth_path(self, points: list[QPointF]) -> QPainterPath:
        path = QPainterPath()
        path.moveTo(points[0])
        if len(points) == 2:
            path.lineTo(points[1])
            return path

        for index in range(1, len(points)):
            previous = points[index - 1]
            current = points[index]
            control_x = (previous.x() + current.x()) / 2
            path.cubicTo(control_x, previous.y(), control_x, current.y(), current.x(), current.y())
        return path


class DataTable(QTableWidget):
    def __init__(self, headers: list[str], parent: QWidget | None = None) -> None:
        super().__init__(0, len(headers), parent)
        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setShowGrid(False)
        self.setAlternatingRowColors(False)
        self.setWordWrap(True)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.horizontalHeader().setStretchLastSection(True)

    def create_item(self, column_index: int, value: str) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def set_rows(self, rows: list[list[str]]) -> None:
        self.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = self.create_item(column_index, value)
                self.setItem(row_index, column_index, item)
            self.setRowHeight(row_index, 44)
        self.resizeColumnsToContents()


class ServicesTable(DataTable):
    def create_item(self, column_index: int, value: str) -> QTableWidgetItem:
        display_value = value
        item = super().create_item(column_index, value)

        if column_index == 0 and value and value != "No inspected services available.":
            display_value = f"●  {value}"
        elif column_index == 1:
            if value.lower() == "running":
                item.setForeground(QColor("#16a34a"))
            elif value.lower() == "stopped":
                item.setForeground(QColor("#dc2626"))
        elif column_index == 2:
            item.setForeground(QColor("#64748b"))

        item.setText(display_value)
        return item


class RequirementsTable(DataTable):
    def create_item(self, column_index: int, value: str) -> QTableWidgetItem:
        item = super().create_item(column_index, value)
        if column_index == 3:
            passed = value.upper() == "PASS"
            item.setText("PASS" if passed else "CHECK")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QColor("#16a34a" if passed else "#f59e0b"))
        return item
