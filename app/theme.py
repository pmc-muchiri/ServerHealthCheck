LIGHT_THEME = """
QWidget {
    background-color: #f6f8fb;
    color: #0b1220;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, QMenuBar, QMenu {
    background-color: #f6f8fb;
    color: #0b1220;
}
#leftMenuSubContainer {
    background-color: #ffffff;
    border-right: 1px solid #d9e1eb;
}
#centralBody {
    background-color: #eef3fb;
}
#headerContainer, #footerContainter {
    background-color: #ffffff;
    border-bottom: 1px solid #d9e1eb;
}
#footerContainter {
    border-top: 1px solid #d9e1eb;
    border-bottom: 0;
}
#rightMenuSubContainer {
    background-color: #ffffff;
    border-left: 1px solid #d9e1eb;
}
#logoBadge {
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: 17px;
    background-color: #0f9696;
    color: white;
    font-weight: 700;
}
QFrame[panel="true"], QFrame[kpi="true"], QFrame[metric="true"] {
    background-color: #ffffff;
    border: 1px solid #d9e1eb;
    border-radius: 14px;
}
QFrame[metric="true"] {
    border-width: 2px;
}
QLabel[title="true"] {
    font-size: 20pt;
    font-weight: 700;
}
QLabel[subtitle="true"], QLabel[muted="true"] {
    color: #60708b;
}
QLabel[section="true"], QLabel[panelTitle="true"] {
    color: #48678f;
    font-weight: 700;
    text-transform: uppercase;
}
QLabel[success="true"] {
    color: #16a34a;
    font-weight: 700;
}
QLabel[danger="true"] {
    color: #dc2626;
    font-weight: 700;
}
QLabel[mono="true"] {
    font-family: Consolas, "Courier New";
}
QPushButton {
    background-color: transparent;
    border: 1px solid #d9e1eb;
    border-radius: 10px;
    padding: 10px 12px;
}
QPushButton:hover {
    background-color: #e9f0ff;
}
QPushButton[primary="true"] {
    background-color: #0f9696;
    border: 1px solid #0f9696;
    color: white;
    font-weight: 700;
}
QPushButton[activeNav="true"] {
    background-color: #1f232a;
    color: white;
    border-color: #1f232a;
}
#menuButton {
    background-color: #1f232a;
    color: white;
    border-color: #1f232a;
}
QLineEdit {
    background-color: #fbfcfe;
    border: 1px solid #d9e1eb;
    border-radius: 10px;
    padding: 10px 12px;
}
QTableWidget {
    background-color: white;
    border: none;
    gridline-color: #e7edf5;
    alternate-background-color: #f8fbff;
}
QHeaderView::section {
    background-color: white;
    color: #48678f;
    border: none;
    border-bottom: 1px solid #d9e1eb;
    padding: 10px;
    font-weight: 700;
}
QTableWidget::item {
    border-bottom: 1px solid #edf2f7;
    padding: 8px 10px;
}
QProgressBar {
    background-color: #e7edf5;
    border: 0;
    border-radius: 5px;
    height: 10px;
}
QProgressBar::chunk {
    background-color: #0f9696;
    border-radius: 5px;
}
"""

DARK_THEME = """
QWidget {
    background-color: #1f232a;
    color: #ffffff;
    font-family: "Segoe UI";
    font-size: 10pt;
}
QMainWindow, QMenuBar, QMenu {
    background-color: #1f232a;
    color: #ffffff;
}
#leftMenuSubContainer {
    background-color: #16191d;
    border-right: 1px solid #2c313c;
}
#centralBody {
    background-color: #1f232a;
}
#headerContainer, #footerContainter {
    background-color: #2c313c;
}
#rightMenuSubContainer {
    background-color: #2c313c;
    border-left: 1px solid #363c49;
}
#logoBadge {
    min-width: 34px;
    max-width: 34px;
    min-height: 34px;
    max-height: 34px;
    border-radius: 17px;
    background-color: #03c3c3;
    color: #16191d;
    font-weight: 700;
}
QFrame[panel="true"], QFrame[kpi="true"], QFrame[metric="true"] {
    background-color: #16191d;
    border: 1px solid #363c49;
    border-radius: 14px;
}
QFrame[metric="true"] {
    border-width: 2px;
}
QLabel[title="true"] {
    font-size: 20pt;
    font-weight: 700;
}
QLabel[subtitle="true"], QLabel[muted="true"] {
    color: #b6c2d3;
}
QLabel[section="true"], QLabel[panelTitle="true"] {
    color: #9eb6d8;
    font-weight: 700;
    text-transform: uppercase;
}
QLabel[success="true"] {
    color: #4ade80;
    font-weight: 700;
}
QLabel[danger="true"] {
    color: #f87171;
    font-weight: 700;
}
QLabel[mono="true"] {
    font-family: Consolas, "Courier New";
}
QPushButton {
    background-color: transparent;
    border: 1px solid #363c49;
    border-radius: 10px;
    padding: 10px 12px;
    color: #ffffff;
    text-align: left;
}
QPushButton:hover {
    background-color: #38404d;
}
QPushButton[primary="true"] {
    background-color: #03c3c3;
    border: 1px solid #03c3c3;
    color: #16191d;
    font-weight: 700;
}
QPushButton[activeNav="true"] {
    background-color: #1f232a;
    color: white;
    border-color: #1f232a;
}
#menuButton {
    background-color: #1f232a;
    color: white;
    border-color: #1f232a;
    text-align: center;
}
QLineEdit {
    background-color: #1f232a;
    border: 1px solid #363c49;
    border-radius: 10px;
    padding: 10px 12px;
}
QTableWidget {
    background-color: #16191d;
    border: none;
    gridline-color: #363c49;
    alternate-background-color: #1b2027;
}
QHeaderView::section {
    background-color: #16191d;
    color: #9eb6d8;
    border: none;
    border-bottom: 1px solid #363c49;
    padding: 10px;
    font-weight: 700;
}
QTableWidget::item {
    border-bottom: 1px solid #2b3240;
    padding: 8px 10px;
}
QProgressBar {
    background-color: #1f232a;
    border: 0;
    border-radius: 5px;
    height: 10px;
}
QProgressBar::chunk {
    background-color: #03c3c3;
    border-radius: 5px;
}
"""
