import os
from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic
from paths import resource_dir

BASE_DIR = resource_dir()
UI_DIR = os.path.join(BASE_DIR, "ui")
IMG_DIR = os.path.join(BASE_DIR, "images")


class NavBar(QFrame):
    """Top navigation bar displayed on all screens except the Login page.

    Loads its layout from navbar.ui and configures the role icon and
    optional search field visibility.

    Args:
        role_text (str): The text label for the user role button
            (e.g., 'Admin' or 'User'). Defaults to 'Admin'.
        show_search (bool): Whether to display the search input field.
            Defaults to False.
        parent (QWidget or None): The parent widget. Defaults to None.
    """

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
