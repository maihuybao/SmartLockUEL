import os
from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")
IMG_DIR = os.path.join(BASE_DIR, "images")


class NavBar(QFrame):
    """Header chung cho mọi màn hình (trừ Login). Load từ navbar.ui."""

    def __init__(self, role_text="Admin", show_search=False, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "navbar.ui"), self)

        # Set role button text + icon
        self.btnRole.setText(role_text)
        icon_file = "admin.png" if role_text == "Admin" else "user.png"
        icon_path = os.path.join(IMG_DIR, icon_file)
        if os.path.exists(icon_path):
            self.btnRole.setIcon(QIcon(icon_path))
            self.btnRole.setIconSize(QSize(20, 20))

        # Show/hide search
        if not show_search:
            self.lineEditSearch.hide()
