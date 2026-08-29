import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from main import main

def run():
    app = QApplication.instance() or QApplication(sys.argv)
    # Create main window but don't show
    from gui.main_window import MainWindow
    w = MainWindow()
    # Quit after 100 ms
    QTimer.singleShot(100, app.quit)
    app.exec()

if __name__ == '__main__':
    run()
