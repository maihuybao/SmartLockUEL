import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QApplication,
    QMessageBox,
    QScrollArea,
    QFrame,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6 import uic

from widgets.navbar import NavBar
from widgets.sidebar import SideBar
from paths import resource_dir

BASE_DIR = resource_dir()
UI_DIR = os.path.join(BASE_DIR, "ui")


class BaseWindow(QMainWindow):
    """
    Window mac dinh chua san NavBar + SideBar.
    Ho tro 2 che do:
      - Che do cu: dung content_area + content_layout (cho User page)
      - Che do stack: dung QStackedWidget (cho Admin shell)
    """

    def __init__(
        self,
        user,
        role_text="Admin",
        show_search=False,
        show_sidebar=True,
        title="SmartLocker UEL",
        use_stack=False,
    ):
        super().__init__()
        self.current_user = user
        self._use_stack = use_stack
        self.setWindowTitle(title)
        self.setMinimumSize(800, 500)
        self.resize(1200, 800)

        # F11 toggle fullscreen
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        shortcut.activated.connect(self._toggle_fullscreen)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # NavBar
        self.navbar = NavBar(role_text=role_text, show_search=show_search)
        main_layout.addWidget(self.navbar)

        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # SideBar (optional)
        self.sidebar = None
        if show_sidebar:
            self.sidebar = SideBar()
            body.addWidget(self.sidebar)

        if use_stack:
            # Che do stack: QStackedWidget thay cho scroll area
            self._stack = QStackedWidget()
            body.addWidget(self._stack, 1)
            self._page_buttons = []
        else:
            # Che do cu: scroll area (cho User page)
            self._scroll = QScrollArea()
            self._scroll.setWidgetResizable(True)
            self._scroll.setFrameShape(QFrame.Shape.NoFrame)
            self._scroll.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self._scroll.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )

            self.content_area = QWidget()
            self.content_layout = QVBoxLayout(self.content_area)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self._scroll.setWidget(self.content_area)
            body.addWidget(self._scroll, 1)

        main_layout.addLayout(body)

    # -- Stack page management (Admin shell) -----------------------

    def add_page(self, page_widget, sidebar_button_name=None):
        """Them page vao stack. Tra ve index cua page."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(page_widget)

        idx = self._stack.addWidget(scroll)
        self._page_buttons.append(sidebar_button_name)
        return idx

    def switch_page(self, index):
        """Chuyen sang page tai index, highlight sidebar button tuong ung."""
        self._stack.setCurrentIndex(index)
        if self.sidebar and index < len(self._page_buttons):
            self._highlight_sidebar(self._page_buttons[index])

    def get_current_scroll_area(self):
        """Tra ve scroll area hien tai (de page tinh layout)."""
        if self._use_stack:
            return self._stack.currentWidget()
        return self._scroll

    # -- Sidebar ---------------------------------------------------

    def _highlight_sidebar(self, active_button_name):
        """Highlight button dang active tren sidebar."""
        nav_buttons = [
            "pushButtonOverview",
            "pushButtonBookings",
            "pushButtonEdit",
            "pushButtonUsers",
            "pushButtonDevices",
        ]
        for name in nav_buttons:
            btn = getattr(self.sidebar, name, None)
            if btn:
                btn.setProperty("active", name == active_button_name)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    # -- Content loading (che do cu, cho User page) ----------------

    def load_content_ui(self, ui_filename):
        """Load file .ui vao content_area (che do cu)."""
        content_widget = QWidget()
        uic.loadUi(os.path.join(UI_DIR, ui_filename), content_widget)
        self.content_layout.addWidget(content_widget)
        return content_widget

    # -- Common actions --------------------------------------------

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _logout(self):
        reply = QMessageBox.question(
            self,
            "Log out",
            "Are you sure you want to log out?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        from controllers.main_window import MainWindowController

        self._login = MainWindowController()
        self._login.show()
        self.close()

    @staticmethod
    def _quit():
        reply = QMessageBox.question(
            None,
            "Quit",
            "Are you sure you want to quit?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
