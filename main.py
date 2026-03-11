import sys
from PyQt6.QtWidgets import QApplication
from controllers.main_window import MainWindowController


def main():
    """Initialize and launch the SmartLocker UEL application.

    Creates the Qt application instance, displays the login window, and
    enters the main event loop. The process exits with the application's
    return code when the event loop terminates.
    """
    app = QApplication(sys.argv)
    window = MainWindowController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
