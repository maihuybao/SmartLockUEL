import os
from PyQt6.QtWidgets import QFrame
from PyQt6 import uic
from paths import resource_dir

BASE_DIR = resource_dir()
UI_DIR = os.path.join(BASE_DIR, "ui")


class SideBar(QFrame):
    """Sidebar chung cho các màn hình Admin. Load từ sidebar.ui."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "sidebar.ui"), self)
