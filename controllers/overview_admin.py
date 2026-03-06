from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QDialog,
    QTableWidgetItem, QPushButton, QHeaderView, QInputDialog,
)
from PyQt6 import uic
import os

from widgets.base_window import BaseWindow
from widgets.room_card import create_room_card
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import get_all_bookings, approve_booking, reject_booking, get_dashboard_stats

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
        self.ui.btnAll.setChecked(True)
        self._load_rooms()

    def _connect_sidebar(self):
        """Override: Overview is current page."""
        self.sidebar.btnOverview.clicked.connect(lambda: None)
        self.sidebar.btnEdit.clicked.connect(self._go_edit)
        self.sidebar.btnUsers.clicked.connect(self._go_users)
        self.sidebar.btnLogout.clicked.connect(self._logout)
        self.sidebar.btnQuit.clicked.connect(QApplication.quit)

    def _connect_signals(self):
        # Filters
        self.ui.btnAll.clicked.connect(lambda: self._apply_filter("All"))
        self.ui.btnAvailable.clicked.connect(lambda: self._apply_filter("Available"))
        self.ui.btnOccupied.clicked.connect(lambda: self._apply_filter("Occupied"))
        self.ui.btnBooked.clicked.connect(lambda: self._apply_filter("Full"))
        self.ui.btnCleaning.clicked.connect(lambda: self._apply_filter("Cleaning"))

        # Search
        self.navbar.lineEditSearch.textChanged.connect(self._on_search)

        # Navbar role button → booking management
        self.navbar.btnRole.clicked.connect(self._show_booking_management)

    # ── Room grid ────────────────────────────────────────

    def _load_rooms(self):
        keyword = ""
        if self.navbar.lineEditSearch:
            keyword = self.navbar.lineEditSearch.text().strip()
        if keyword:
            rooms = search_rooms(keyword)
        elif self._current_filter == "All":
            rooms = get_all_rooms()
        else:
            rooms = get_rooms_by_status(self._current_filter)
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

        card_min_w = 180
        spacing = layout.horizontalSpacing() or 10
        available = self.content_area.width() - 20  # margins
        cols = max(1, available // (card_min_w + spacing))

        for i, room in enumerate(self._rooms_data):
            card = self._create_room_card(room)
            layout.addWidget(card, i // cols, i % cols)

    def showEvent(self, event):
        super().showEvent(event)
        self._reflow_grid()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reflow_grid()

    def _create_room_card(self, room):
        return create_room_card(room)

    def _apply_filter(self, status):
        self._current_filter = status
        self._load_rooms()

    def _on_search(self):
        self._load_rooms()

    # ── Booking Management ───────────────────────────────

    def _show_booking_management(self):
        dlg = QDialog(self)
        uic.loadUi(os.path.join(UI_DIR, "BookingApproval.ui"), dlg)
        dlg.tableBookings.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        dlg.btnClose.clicked.connect(dlg.accept)
        dlg.comboFilter.currentTextChanged.connect(
            lambda f: self._populate_approvals(dlg, f)
        )
        self._populate_approvals(dlg, "All Status")
        dlg.exec()

    def _populate_approvals(self, dlg, filter_text):
        bookings = get_all_bookings()
        stats = get_dashboard_stats()

        dlg.lblTotalVal.setText(str(stats["total_bookings"]))
        dlg.lblPendingVal.setText(str(stats["pending"]))
        dlg.lblApprovedVal.setText(str(stats["approved"]))
        dlg.lblRejectedVal.setText(str(stats["rejected"]))

        if filter_text != "All Status":
            bookings = [b for b in bookings if b["status"] == filter_text]

        table = dlg.tableBookings
        table.setRowCount(len(bookings))
        for row, b in enumerate(bookings):
            table.setItem(row, 0, QTableWidgetItem(b["username"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 2, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 3, QTableWidgetItem(b["session"]))
            table.setItem(row, 4, QTableWidgetItem(b["reason"]))
            table.setItem(row, 5, QTableWidgetItem(b["status"]))
            table.setCellWidget(row, 6, None)
            table.setCellWidget(row, 7, None)

            if b["status"] == "Pending":
                btn_approve = QPushButton("Approve")
                btn_approve.setStyleSheet(
                    "background:#4CAF50;color:white;border-radius:4px;padding:4px;"
                )
                btn_approve.clicked.connect(
                    lambda _, bid=b["id"]: self._approve(bid, dlg)
                )
                table.setCellWidget(row, 6, btn_approve)

                btn_reject = QPushButton("Reject")
                btn_reject.setStyleSheet(
                    "background:#F44336;color:white;border-radius:4px;padding:4px;"
                )
                btn_reject.clicked.connect(
                    lambda _, bid=b["id"]: self._reject(bid, dlg)
                )
                table.setCellWidget(row, 7, btn_reject)

        dlg.lblCount.setText(f"{len(bookings)} bookings")

    def _approve(self, booking_id, dlg):
        password = approve_booking(booking_id)
        QMessageBox.information(
            self, "Approved",
            f"Booking approved.\nLocker password: {password}",
        )
        self._populate_approvals(dlg, dlg.comboFilter.currentText())
        self._load_rooms()

    def _reject(self, booking_id, dlg):
        reason, ok = QInputDialog.getText(
            self, "Reject", "Enter rejection reason:"
        )
        if ok and reason.strip():
            reject_booking(booking_id, reason.strip())
            QMessageBox.information(self, "Rejected", "Booking has been rejected.")
            self._populate_approvals(dlg, dlg.comboFilter.currentText())
            self._load_rooms()
