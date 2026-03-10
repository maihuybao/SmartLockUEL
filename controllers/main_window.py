import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QSizePolicy,
)
from PyQt6.QtGui import QIcon, QPixmap, QKeySequence, QShortcut, QPainter
from PyQt6.QtCore import QSize, Qt
from PyQt6 import uic

from database import init_db
from models.user_model import authenticate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")
IMG_DIR = os.path.join(BASE_DIR, "images")


class _BgWidget:
    """Mixin vẽ background.jpg scale-to-cover (giữ tỉ lệ) cho centralwidget."""

    _bg_pixmap = None

    def paintEvent(self, event):
        if self._bg_pixmap:
            painter = QPainter(self)
            scaled = self._bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            super().paintEvent(event)


class MainWindowController(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(UI_DIR, "Login.ui"), self)
        self.setMinimumSize(1000, 600)
        self.resize(1200, 800)
        init_db()

        # F11 toggle fullscreen
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        shortcut.activated.connect(self._toggle_fullscreen)

        self._setup_background()
        self._make_login_responsive()

        self._password_visible = False
        self._logging_in = False
        self._setup_ui()
        self._connect_signals()

    def _setup_background(self):
        bg_path = os.path.join(IMG_DIR, "background.jpg")
        if not os.path.exists(bg_path):
            return
        pixmap = QPixmap(bg_path)
        central = self.centralwidget
        central.setStyleSheet("")
        central.__class__ = type(
            "BgCentral",
            (_BgWidget, central.__class__),
            {},
        )
        central._bg_pixmap = pixmap

    def _make_login_responsive(self):
        form = self.widget
        form.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # Đảm bảo card login có nền trắng rõ trên ảnh nền
        form.setStyleSheet(
            "QWidget#widget { background: rgba(255,255,255,0.92); "
            "border-radius: 12px; }"
        )

    def _setup_ui(self):
        # Fix logo path
        logo_path = os.path.join(IMG_DIR, "UEL_Logo final-09.png")
        if os.path.exists(logo_path):
            self.label.setPixmap(
                QPixmap(logo_path).scaled(
                    120,
                    120,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

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
        if self._logging_in:
            return
        self._logging_in = True

        email = self.lineEditEmail.text().strip()
        password = self.lineEditPassword.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Please enter your email and password.")
            self._logging_in = False
            return

        user = authenticate(email, password)
        if not user:
            QMessageBox.warning(self, "Error", "Incorrect email or password.")
            self._logging_in = False
            return

        selected_role = "admin" if self.radioButtonAdmin.isChecked() else "user"
        if user["role"] != selected_role:
            QMessageBox.warning(
                self,
                "Error",
                f"This account does not have '{selected_role}' permission.",
            )
            self._logging_in = False
            return

        self._open_dashboard(user)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _open_dashboard(self, user):
        if user["role"] == "admin":
            from controllers.overview_admin import OverviewAdminController

            self._dashboard = OverviewAdminController(user)
        else:
            from controllers.overview_users import OverviewUsersController

            self._dashboard = OverviewUsersController(user)

        self._dashboard.show()
        self.close()
