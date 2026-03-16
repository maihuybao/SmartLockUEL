import os
from PyQt6.QtWidgets import QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic
from paths import resource_dir
from i18n import tr, get_manager

BASE_DIR = resource_dir()
UI_DIR = os.path.join(BASE_DIR, "ui")
IMG_DIR = os.path.join(BASE_DIR, "images")


class NavBar(QFrame):
    """Top navigation bar displayed on all screens except the Login page.

    Loads its layout from navbar.ui and configures the role icon,
    optional search field visibility, and language toggle button.

    Args:
        role_text (str): The text label for the user role button
            (e.g., 'Admin' or 'User'). Defaults to 'Admin'.
        show_search (bool): Whether to display the search input field.
            Defaults to False.
        parent (QWidget or None): The parent widget. Defaults to None.
    """

    def __init__(self, role_text="Admin", show_search=False, parent=None):
        """Initialize the navigation bar from its UI file and configure widgets."""
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "navbar.ui"), self)

        self._role_key = "role_admin" if role_text == "Admin" else "role_user"
        self._is_admin = role_text == "Admin"

        # Set role button text + icon
        self.btnRole.setText(tr(self._role_key))
        icon_file = "admin.png" if self._is_admin else "user.png"
        icon_path = os.path.join(IMG_DIR, icon_file)
        if os.path.exists(icon_path):
            self.btnRole.setIcon(QIcon(icon_path))
            self.btnRole.setIconSize(QSize(20, 20))

        # Show/hide search
        if not show_search:
            self.lineEditSearch.hide()

        # Language toggle
        self._update_lang_btn()
        self.btnLang.clicked.connect(self._toggle_lang)

    def _toggle_lang(self):
        mgr = get_manager()
        new_lang = "vi" if mgr.current_language() == "en" else "en"
        mgr.set_language(new_lang)

    def _update_lang_btn(self):
        mgr = get_manager()
        self.btnLang.setText("VI" if mgr.current_language() == "en" else "EN")

    def retranslate_ui(self):
        self.labelTitle.setText(tr("app_title"))
        self.lineEditSearch.setPlaceholderText(tr("search_placeholder"))
        self.btnRole.setText(tr(self._role_key))
        self._update_lang_btn()
