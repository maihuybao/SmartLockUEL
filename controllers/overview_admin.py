from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6 import uic
import os

from widgets.room_card import create_room_card, get_display_status
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import get_dashboard_stats
from paths import resource_dir

BASE_DIR = resource_dir()
UI_DIR = os.path.join(BASE_DIR, "ui")


class OverviewAdminPage(QWidget):
    """Admin overview page displaying room cards and dashboard statistics.

    Shows a filterable grid of room cards (All/Available/Occupied/Full) with
    live search integration via the admin shell's navbar.

    Args:
        shell (AdminShellController): The parent admin shell controller
            providing navbar and navigation access.
    """

    def __init__(self, shell):
        """Initialize the overview page, load UI, and display initial data."""
        super().__init__()
        self._shell = shell
        self._current_filter = "All"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.ui = QWidget()
        uic.loadUi(os.path.join(UI_DIR, "OverviewAdmin.ui"), self.ui)
        layout.addWidget(self.ui)

        self._connect_signals()
        self.ui.pushButtonAll.setChecked(True)
        self._load_stats()
        self._load_rooms()

    def _connect_signals(self):
        """Connect filter buttons and search field to their handler methods."""
        self.ui.pushButtonAll.clicked.connect(lambda: self._apply_filter("All"))
        self.ui.pushButtonAvailable.clicked.connect(
            lambda: self._apply_filter("Available")
        )
        self.ui.pushButtonOccupied.clicked.connect(
            lambda: self._apply_filter("Occupied")
        )
        self.ui.pushButtonBooked.clicked.connect(lambda: self._apply_filter("Full"))

        # Search tu navbar cua shell
        self._shell.navbar.lineEditSearch.textChanged.connect(self._on_search)

    # -- Room grid ------------------------------------------------

    def refresh(self):
        """Reload dashboard statistics and room cards from the database."""
        self._load_stats()
        self._load_rooms()

    def _load_rooms(self):
        """Load rooms from the database applying current filter and search criteria."""
        keyword = ""
        if self._shell.navbar.lineEditSearch:
            keyword = self._shell.navbar.lineEditSearch.text().strip()
        if keyword:
            rooms = search_rooms(keyword)
        elif self._current_filter == "Full":
            rooms = [r for r in get_all_rooms() if get_display_status(r) == "Full"]
        elif self._current_filter == "All":
            rooms = get_all_rooms()
        else:
            rooms = get_rooms_by_status(self._current_filter)

        if self._current_filter == "Available":
            rooms = [r for r in rooms if get_display_status(r) != "Full"]
        self._render_room_cards(rooms)

    def _render_room_cards(self, rooms):
        """Store room data and trigger a grid reflow to display room cards.

        Args:
            rooms (list[dict]): The list of room dictionaries to render.
        """
        self._rooms_data = rooms
        self._reflow_grid()

    def _reflow_grid(self):
        """Recalculate the grid layout and re-render all room cards.

        Adjusts the number of columns based on the available widget width
        to create a responsive card grid.
        """
        if not hasattr(self, "_rooms_data"):
            return
        layout = self.ui.gridLayout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        card_w = 200
        spacing = layout.horizontalSpacing() or 10
        available = self.width() - 20
        cols = max(1, available // (card_w + spacing))

        for i, room in enumerate(self._rooms_data):
            card = self._create_room_card(room)
            layout.addWidget(card, i // cols, i % cols)

        last_row = (len(self._rooms_data) - 1) // cols if self._rooms_data else 0
        layout.setRowStretch(last_row + 1, 1)
        layout.setColumnStretch(cols, 1)

    def showEvent(self, event):
        """Handle the widget show event by reflowing the room card grid."""
        super().showEvent(event)
        self._reflow_grid()

    def resizeEvent(self, event):
        """Handle the widget resize event by reflowing the room card grid."""
        super().resizeEvent(event)
        self._reflow_grid()

    def _create_room_card(self, room):
        """Create a room card widget with an attached context menu.

        Args:
            room (dict): The room dictionary to create a card for.

        Returns:
            QWidget: The room card widget.
        """
        return create_room_card(room, on_context=self._on_card_context)

    def _on_card_context(self, room, global_pos):
        """Display a context menu with an 'Edit Room' action for a room card.

        Args:
            room (dict): The room dictionary for the right-clicked card.
            global_pos (QPoint): The global screen position for the context menu.
        """
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction

        menu = QMenu(self)
        act = QAction("Edit Room", self)
        act.triggered.connect(lambda: self._shell.go_to_rooms(preselect_room=room))
        menu.addAction(act)
        menu.exec(global_pos)

    def _apply_filter(self, status):
        """Apply a room status filter and reload the room grid.

        Args:
            status (str): The status filter to apply. One of 'All',
                'Available', 'Occupied', or 'Full'.
        """
        self._current_filter = status
        self._load_rooms()

    def _on_search(self):
        """Handle search input changes by reloading the room grid."""
        self._load_rooms()

    def _load_stats(self):
        """Load and display dashboard statistics (room and booking counts)."""
        stats = get_dashboard_stats()
        self.ui.lblTotalRoomsVal.setText(str(stats["total_rooms"]))
        self.ui.lblTotalBookingsVal.setText(str(stats["total_bookings"]))
        self.ui.lblPendingVal.setText(str(stats["pending"]))
        self.ui.lblApprovedVal.setText(str(stats["approved"]))
        self.ui.lblRejectedVal.setText(str(stats["rejected"]))
