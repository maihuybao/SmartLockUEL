import os
from PyQt6.QtWidgets import QFrame
from PyQt6 import uic

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")


class SideBar(QFrame):
    """Sidebar chung cho các màn hình Admin. Load từ sidebar.ui."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "sidebar.ui"), self)
