import os
from PyQt6.QtWidgets import QFrame
from PyQt6 import uic
from paths import resource_dir
from i18n import tr

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
        """Initialize the sidebar from its UI file."""
        super().__init__(parent)
        uic.loadUi(os.path.join(UI_DIR, "sidebar.ui"), self)

    def retranslate_ui(self):
        self.pushButtonOverview.setText(tr("sidebar_dashboard"))
        self.pushButtonBookings.setText(tr("sidebar_bookings"))
        self.pushButtonEdit.setText(tr("sidebar_rooms"))
        self.pushButtonUsers.setText(tr("sidebar_users"))
        self.pushButtonDevices.setText(tr("sidebar_devices"))
        self.pushButtonLogOut.setText(tr("sidebar_logout"))
        self.pushButtonQuit.setText(tr("sidebar_quit"))
