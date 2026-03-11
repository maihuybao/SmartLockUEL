import os
from PyQt6.QtWidgets import QFrame
from PyQt6 import uic
from paths import resource_dir

BASE_DIR = resource_dir()
UI_DIR = os.path.join(BASE_DIR, "ui")


class SideBar(QFrame):
    """Sidebar navigation panel for Admin screens.

    Loads its layout from sidebar.ui and provides navigation buttons
    for switching between admin management pages.

    Args:
        parent (QWidget or None): The parent widget. Defaults to None.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "sidebar.ui"), self)
