import sys
from PyQt6.QtWidgets import QApplication
from controllers.main_window import MainWindowController


def main():
    app = QApplication(sys.argv)
    window = MainWindowController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
