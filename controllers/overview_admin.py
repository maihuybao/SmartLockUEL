from PyQt6.QtWidgets import QApplication
from PyQt6 import uic
import os

from widgets.base_window import BaseWindow
from widgets.room_card import create_room_card, get_display_status
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import get_dashboard_stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")


class OverviewAdminController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=True,
            show_sidebar=True, title="SmartLocker UEL - Admin",
        )
        self._current_filter = "All"

        # Load content from .ui
        self.ui = self.load_content_ui("OverviewAdmin.ui")

        self._connect_signals()
        self.ui.pushButtonAll.setChecked(True)
        self._load_stats()
        self._load_rooms()

    def _connect_sidebar(self):
        """Override: Overview is current page."""
        self.sidebar.pushButtonOverview.clicked.connect(lambda: None)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(self._go_edit)
        self.sidebar.pushButtonUsers.clicked.connect(self._go_users)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        # Filters
        self.ui.pushButtonAll.clicked.connect(lambda: self._apply_filter("All"))
        self.ui.pushButtonAvailable.clicked.connect(lambda: self._apply_filter("Available"))
        self.ui.pushButtonOccupied.clicked.connect(lambda: self._apply_filter("Occupied"))
        self.ui.pushButtonBooked.clicked.connect(lambda: self._apply_filter("Full"))

        # Search
        self.navbar.lineEditSearch.textChanged.connect(self._on_search)

    # ── Room grid ────────────────────────────────────────

    def _load_rooms(self):
        keyword = ""
        if self.navbar.lineEditSearch:
            keyword = self.navbar.lineEditSearch.text().strip()
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
        self._rooms_data = rooms
        self._reflow_grid()

    def _reflow_grid(self):
        if not hasattr(self, '_rooms_data'):
            return
        layout = self.ui.gridLayout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        card_w = 200
        spacing = layout.horizontalSpacing() or 10
        available = self.content_area.width() - 20
        cols = max(1, available // (card_w + spacing))

        for i, room in enumerate(self._rooms_data):
            card = self._create_room_card(room)
            layout.addWidget(card, i // cols, i % cols)

        # Stretch cuối để đẩy card về góc trên-trái
        last_row = (len(self._rooms_data) - 1) // cols if self._rooms_data else 0
        layout.setRowStretch(last_row + 1, 1)
        layout.setColumnStretch(cols, 1)

    def showEvent(self, event):
        super().showEvent(event)
        self._reflow_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow_grid()

    def _create_room_card(self, room):
        return create_room_card(room, on_context=self._on_card_context)

    def _on_card_context(self, room, global_pos):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        menu = QMenu(self)
        act = QAction("Edit Room", self)
        act.triggered.connect(lambda: self._go_edit(preselect_room=room))
        menu.addAction(act)
        menu.exec(global_pos)

    def _apply_filter(self, status):
        self._current_filter = status
        self._load_rooms()

    def _on_search(self):
        self._load_rooms()

    def _load_stats(self):
        stats = get_dashboard_stats()
        self.ui.lblTotalRoomsVal.setText(str(stats["total_rooms"]))
        self.ui.lblTotalBookingsVal.setText(str(stats["total_bookings"]))
        self.ui.lblPendingVal.setText(str(stats["pending"]))
        self.ui.lblApprovedVal.setText(str(stats["approved"]))
        self.ui.lblRejectedVal.setText(str(stats["rejected"]))
