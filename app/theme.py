LIGHT_THEME = """
QWidget {
    background-color: #f6f8fa;
    color: #1f2328;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, QMenuBar, QMenu {
    background-color: #f6f8fa;
    color: #1f2328;
}
QMenuBar {
    border-bottom: 1px solid #d0d7de;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
}
QMenuBar::item:selected, QMenu::item:selected {
    background-color: #f3f4f6;
}
#leftMenuSubContainer {
    background-color: #ffffff;
    border-right: 1px solid #d0d7de;
}
#centralBody {
    background-color: #f6f8fa;
}
#headerContainer, #footerContainter {
    background-color: #ffffff;
    border-bottom: 1px solid #d0d7de;
}
#footerContainter {
    border-top: 1px solid #d0d7de;
    border-bottom: 0;
}
#rightMenuSubContainer {
    background-color: #ffffff;
    border-left: 1px solid #d0d7de;
}
#logoBadge {
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    border-radius: 16px;
    background-color: #1f6feb;
    color: #ffffff;
    border: 1px solid #1b5fc7;
    font-weight: 700;
}
QFrame[panel="true"], QFrame[kpi="true"], QFrame[metric="true"] {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
}
QFrame[metric="true"] {
    border-width: 1px;
}
QLabel[title="true"] {
    font-size: 17pt;
    font-weight: 700;
}
QLabel[subtitle="true"], QLabel[muted="true"] {
    color: #656d76;
}
QLabel[section="true"], QLabel[panelTitle="true"] {
    color: #57606a;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
QLabel[success="true"] {
    color: #1a7f37;
    font-weight: 700;
}
QLabel[danger="true"] {
    color: #cf222e;
    font-weight: 700;
}
QLabel[mono="true"] {
    font-family: Consolas, "Courier New";
}
QPushButton {
    background-color: #f6f8fa;
    color: #24292f;
    border: 1px solid rgba(31, 35, 40, 0.15);
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 600;
    text-align: left;
}
QPushButton:hover {
    background-color: #f3f4f6;
}
QPushButton:pressed {
    background-color: #ebecf0;
}
QPushButton[primary="true"] {
    background-color: #2da44e;
    border: 1px solid rgba(31, 35, 40, 0.15);
    color: #ffffff;
    font-weight: 700;
}
QPushButton[primary="true"]:hover {
    background-color: #2c974b;
}
QPushButton[activeNav="true"] {
    background-color: #edf3ff;
    color: #0969da;
    border-color: #b6d2ff;
}
#menuButton {
    background-color: #ffffff;
    color: #57606a;
    border-color: #d0d7de;
    text-align: center;
}
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #0969da;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border: 1px solid #0969da;
}
QTableWidget {
    background-color: #ffffff;
    border: none;
    gridline-color: #d8dee4;
    alternate-background-color: #f6f8fa;
}
QHeaderView::section {
    background-color: #f6f8fa;
    color: #57606a;
    border: none;
    border-bottom: 1px solid #d0d7de;
    padding: 8px 10px;
    font-weight: 700;
}
QTableWidget::item {
    border-bottom: 1px solid #d8dee4;
    padding: 8px 10px;
}
QProgressBar {
    background-color: #eaeef2;
    border: 0;
    border-radius: 4px;
    height: 8px;
}
QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 4px;
}
"""

DARK_THEME = """
QWidget {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, QMenuBar, QMenu {
    background-color: #0d1117;
    color: #e6edf3;
}
QMenuBar {
    border-bottom: 1px solid #30363d;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
}
QMenuBar::item:selected, QMenu::item:selected {
    background-color: #161b22;
}
#leftMenuSubContainer {
    background-color: #010409;
    border-right: 1px solid #30363d;
}
#centralBody {
    background-color: #0d1117;
}
#headerContainer, #footerContainter {
    background-color: #010409;
    border-bottom: 1px solid #30363d;
}
#footerContainter {
    border-top: 1px solid #30363d;
    border-bottom: 0;
}
#rightMenuSubContainer {
    background-color: #010409;
    border-left: 1px solid #30363d;
}
#logoBadge {
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    border-radius: 16px;
    background-color: #1f6feb;
    color: #ffffff;
    border: 1px solid #388bfd;
    font-weight: 700;
}
QFrame[panel="true"], QFrame[kpi="true"], QFrame[metric="true"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
}
QFrame[metric="true"] {
    border-width: 1px;
}
QLabel[title="true"] {
    font-size: 17pt;
    font-weight: 700;
}
QLabel[subtitle="true"], QLabel[muted="true"] {
    color: #8b949e;
}
QLabel[section="true"], QLabel[panelTitle="true"] {
    color: #8b949e;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
QLabel[success="true"] {
    color: #3fb950;
    font-weight: 700;
}
QLabel[danger="true"] {
    color: #f85149;
    font-weight: 700;
}
QLabel[mono="true"] {
    font-family: Consolas, "Courier New";
}
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
    font-weight: 600;
    text-align: left;
}
QPushButton:hover {
    background-color: #30363d;
}
QPushButton:pressed {
    background-color: #262c36;
}
QPushButton[primary="true"] {
    background-color: #238636;
    border: 1px solid rgba(240, 246, 252, 0.1);
    color: #ffffff;
    font-weight: 700;
}
QPushButton[primary="true"]:hover {
    background-color: #2ea043;
}
QPushButton[activeNav="true"] {
    background-color: #0d419d;
    color: #ffffff;
    border-color: #1f6feb;
}
#menuButton {
    background-color: #161b22;
    color: #8b949e;
    border-color: #30363d;
    text-align: center;
}
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
}
QLineEdit:focus {
    border: 1px solid #1f6feb;
}
QTableWidget {
    background-color: #161b22;
    border: none;
    gridline-color: #30363d;
    alternate-background-color: #0d1117;
}
QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    border: none;
    border-bottom: 1px solid #30363d;
    padding: 8px 10px;
    font-weight: 700;
}
QTableWidget::item {
    border-bottom: 1px solid #30363d;
    padding: 8px 10px;
}
QProgressBar {
    background-color: #21262d;
    border: 0;
    border-radius: 4px;
    height: 8px;
}
QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 4px;
}
"""
