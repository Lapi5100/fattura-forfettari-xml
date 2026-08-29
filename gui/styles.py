APP_STYLESHEET = """
QWidget {
    background-color: #E6F0FF;
    color: #333;
}
QGroupBox {
    border: 2px solid #3B82F6;
    border-radius: 8px;
    margin-top: 10px;
    font-weight: bold;
    color: #1E3A5F;
    background-color: #F0F7FF;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QPushButton {
    background-color: #FF6B00;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #E55A00;
}
QTabWidget::pane {
    border: 2px solid #3B82F6;
    background-color: #F0F7FF;
    border-radius: 4px;
}
QTabBar::tab {
    background: #BFDBFE;
    color: #1E3A5F;
    padding: 8px 20px;
    margin-right: 4px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background: #3B82F6;
    color: white;
}
QLineEdit, QComboBox, QDateEdit {
    background-color: white;
    border: 1px solid #93C5FD;
    border-radius: 4px;
    padding: 4px;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: white;
    selection-background-color: #3B82F6;
}
QTableWidget {
    background-color: white;
    gridline-color: #93C5FD;
    alternate-background-color: #EFF6FF;
}
QHeaderView::section {
    background-color: #3B82F6;
    color: white;
    padding: 5px;
    font-weight: bold;
    border: 1px solid #2563EB;
}
QCheckBox {
    color: #1E3A5F;
    font-weight: bold;
}
QCheckBox::indicator:checked {
    background-color: #FF6B00;
    border: 2px solid #FF6B00;
}
"""
