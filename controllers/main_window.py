import os
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize
from PyQt6 import uic

from database import init_db
from models.user_model import authenticate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")
IMG_DIR = os.path.join(BASE_DIR, "images")


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Login.ui"), self)
        self.setFixedSize(1000, 600)
        init_db()

        self._password_visible = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        # Fix logo path
        logo_path = os.path.join(IMG_DIR, "UEL_Logo final-09.png")
        if os.path.exists(logo_path):
            from PyQt6.QtCore import Qt
            self.label.setPixmap(QPixmap(logo_path).scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

        # Fix eye icon
        self._eye_closed = QIcon(os.path.join(IMG_DIR, "eye_closed.png"))
        self._eye_open = QIcon(os.path.join(IMG_DIR, "eye_open.png"))
        self.btnTogglePassword.setIcon(self._eye_closed)
        self.btnTogglePassword.setIconSize(QSize(30, 30))

        # Fix input text color
        input_style = "color: black; font-size: 13px;"
        placeholder_style = "QLineEdit::placeholder { color: #9aa0a6; }"
        for widget in [self.lineEditEmail, self.lineEditPassword]:
            current = widget.styleSheet()
            widget.setStyleSheet(current + input_style + placeholder_style)

    def _connect_signals(self):
        self.pushButtonLogin.clicked.connect(self._handle_login)
        self.btnTogglePassword.clicked.connect(self._toggle_password)
        self.lineEditPassword.returnPressed.connect(self._handle_login)
        self.lineEditEmail.returnPressed.connect(self._handle_login)

    def _toggle_password(self):
        from PyQt6.QtWidgets import QLineEdit
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.lineEditPassword.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btnTogglePassword.setIcon(self._eye_open)
        else:
            self.lineEditPassword.setEchoMode(QLineEdit.EchoMode.Password)
            self.btnTogglePassword.setIcon(self._eye_closed)

    def _handle_login(self):
        email = self.lineEditEmail.text().strip()
        password = self.lineEditPassword.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu.")
            return

        user = authenticate(email, password)
        if not user:
            QMessageBox.warning(self, "Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")
            return

        # Check role matches radio button selection
        selected_role = "admin" if self.radioButtonAdmin.isChecked() else "user"
        if user["role"] != selected_role:
            QMessageBox.warning(
                self, "Lỗi",
                f"Tài khoản này không có quyền '{selected_role}'."
            )
            return

        self._open_dashboard(user)

    def _open_dashboard(self, user):
        if user["role"] == "admin":
            from controllers.overview_admin import OverviewAdminController
            self._dashboard = OverviewAdminController(user)
        else:
            from controllers.overview_users import OverviewUsersController
            self._dashboard = OverviewUsersController(user)

        self._dashboard.show()
        self.close()
