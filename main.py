import sys
from PySide6.QtWidgets import QApplication
from views.simulator_window import MainWindow

if __name__ == '__main__':
    """ The main entry point for the fNIRS Simulator application. """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())