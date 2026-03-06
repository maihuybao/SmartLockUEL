import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication,
)
from PyQt6 import uic

from widgets.navbar import NavBar
from widgets.sidebar import SideBar

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")


class BaseWindow(QMainWindow):
    """
    Window mặc định chứa sẵn NavBar + SideBar.
    Các controller kế thừa class này, chỉ cần:
      1. Gọi super().__init__(...)
      2. Load .ui content vào self.content_area
         hoặc tự build content bằng code rồi add vào self.content_layout
    """

    def __init__(self, user, role_text="Admin", show_search=False,
                 show_sidebar=True, title="SmartLocker UEL"):
        super().__init__()
        self.current_user = user
        self.setWindowTitle(title)
        self.setFixedSize(1000, 600)

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

        # Content area — controllers sẽ add widget vào đây
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        body.addWidget(self.content_area)

        main_layout.addLayout(body)

    def _connect_sidebar(self):
        """Kết nối sidebar navigation mặc định. Override nếu cần."""
        self.sidebar.btnOverview.clicked.connect(self._go_overview)
        self.sidebar.btnEdit.clicked.connect(self._go_edit)
        self.sidebar.btnUsers.clicked.connect(self._go_users)
        self.sidebar.btnLogout.clicked.connect(self._logout)
        self.sidebar.btnQuit.clicked.connect(QApplication.quit)

    def load_content_ui(self, ui_filename):
        """Load file .ui vào content_area."""
        content_widget = QWidget()
        uic.loadUi(os.path.join(UI_DIR, ui_filename), content_widget)
        self.content_layout.addWidget(content_widget)
        return content_widget

    # ── Navigation mặc định ──────────────────────────────

    def _go_overview(self):
        from controllers.overview_admin import OverviewAdminController
        self._win = OverviewAdminController(self.current_user)
        self._win.show()
        self.close()

    def _go_edit(self):
        from controllers.edit_room import EditRoomController
        self._win = EditRoomController(self.current_user)
        self._win.show()
        self.close()

    def _go_users(self):
        from controllers.users_management import UsersManagementController
        self._win = UsersManagementController(self.current_user)
        self._win.show()
        self.close()

    def _logout(self):
        from controllers.main_window import MainWindowController
        self._login = MainWindowController()
        self._login.show()
        self.close()
