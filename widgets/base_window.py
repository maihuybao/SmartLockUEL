import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication,
    QMessageBox, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6 import uic

from widgets.navbar import NavBar
from widgets.sidebar import SideBar

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")


class BaseWindow(QMainWindow):
    """
    Window mac dinh chua san NavBar + SideBar.
    Cac controller ke thua class nay, chi can:
      1. Goi super().__init__(...)
      2. Load .ui content vao self.content_area
         hoac tu build content bang code roi add vao self.content_layout
    """

    def __init__(self, user, role_text="Admin", show_search=False,
                 show_sidebar=True, title="SmartLocker UEL"):
        super().__init__()
        self.current_user = user
        self.setWindowTitle(title)
        self.setMinimumSize(800, 500)
        self.resize(1000, 600)

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
            self._connect_sidebar()

        # Content area — wrapped in scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll.setWidget(self.content_area)
        body.addWidget(self._scroll, 1)

        main_layout.addLayout(body)

    def _connect_sidebar(self):
        """Ket noi sidebar navigation mac dinh. Override neu can."""
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(self._go_edit)
        self.sidebar.pushButtonUsers.clicked.connect(self._go_users)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def load_content_ui(self, ui_filename):
        """Load file .ui vao content_area."""
        content_widget = QWidget()
        uic.loadUi(os.path.join(UI_DIR, ui_filename), content_widget)
        self.content_layout.addWidget(content_widget)
        return content_widget

    # -- Navigation -------------------------------------------

    def _go_overview(self):
        from controllers.overview_admin import OverviewAdminController
        self._win = OverviewAdminController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_bookings(self):
        from controllers.booking_overview import BookingOverviewController
        self._win = BookingOverviewController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_edit(self, preselect_room=None):
        from controllers.edit_room import EditRoomController
        self._win = EditRoomController(self.current_user, preselect_room=preselect_room)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_users(self):
        from controllers.users_management import UsersManagementController
        self._win = UsersManagementController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_devices(self):
        from controllers.device_management import DeviceManagementController
        self._win = DeviceManagementController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _transfer_window_state(self, target):
        if self.isFullScreen():
            target.showFullScreen()
        elif self.isMaximized():
            target.showMaximized()
        else:
            target.resize(self.size())
            target.move(self.pos())

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _logout(self):
        reply = QMessageBox.question(self, "Log out", "Are you sure you want to log out?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        from controllers.main_window import MainWindowController
        self._login = MainWindowController()
        self._login.show()
        self.close()

    @staticmethod
    def _quit():
        reply = QMessageBox.question(
            None, "Quit", "Are you sure you want to quit?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
