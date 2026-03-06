import os
from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")
IMG_DIR = os.path.join(BASE_DIR, "images")


class SideBar(QFrame):
    """Sidebar chung cho các màn hình Admin. Load từ sidebar.ui."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "sidebar.ui"), self)

        # Fix icon paths (relative paths in .ui may not resolve correctly)
        icon_map = {
            "btnOverview": "overview.png",
            "btnEdit": "edit.png",
            "btnUsers": "users.png",
            "btnLogout": "log out.png",
            "btnQuit": "quit.png",
        }
        for name, filename in icon_map.items():
            btn = getattr(self, name, None)
            if btn:
                path = os.path.join(IMG_DIR, filename)
                if os.path.exists(path):
                    btn.setIcon(QIcon(path))
                    btn.setIconSize(QSize(20, 20))
