from PyQt6.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os

from widgets.base_window import BaseWindow
from widgets.room_card import create_room_card, SESSIONS, get_display_status
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import (
    create_booking,
    get_bookings_by_user,
    cancel_booking,
    get_bookings_by_room,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")


class OverviewUsersController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user,
            role_text="User",
            show_search=True,
            show_sidebar=False,
            title="SmartLocker UEL - User",
        )
        self._current_filter = "All"

        # Load content from .ui
        self.ui = self.load_content_ui("OverviewUsers.ui")

        self._connect_signals()
        self.ui.btnAll.setChecked(True)
        self._load_rooms()

    def _connect_signals(self):
        # Filters
        self.ui.btnAll.clicked.connect(lambda: self._apply_filter("All"))
        self.ui.btnAvailable.clicked.connect(lambda: self._apply_filter("Available"))
        self.ui.btnOccupied.clicked.connect(lambda: self._apply_filter("Occupied"))
        self.ui.btnBooked.clicked.connect(lambda: self._apply_filter("Full"))
        self.ui.btnCleaning.clicked.connect(lambda: self._apply_filter("Cleaning"))

        # Search
        self.navbar.lineEditSearch.textChanged.connect(self._on_search)

        # Navbar role button → history
        self.navbar.btnRole.clicked.connect(self._show_history)

        # Bottom bar
        self.ui.btnBooking.clicked.connect(self._open_booking_dialog)
        self.ui.btnLogout.clicked.connect(self._logout)
        self.ui.btnQuit.clicked.connect(self._quit)

    # ── Room grid ────────────────────────────────────────

    def _load_rooms(self):
        keyword = ""
        if self.navbar.lineEditSearch:
            keyword = self.navbar.lineEditSearch.text().strip()
        if keyword:
            rooms = search_rooms(keyword)
        elif self._current_filter == "All":
            rooms = get_all_rooms()
        elif self._current_filter == "Full":
            rooms = [r for r in get_all_rooms() if get_display_status(r) == "Full"]
        else:
            rooms = get_rooms_by_status(self._current_filter)
            if self._current_filter == "Available":
                rooms = [r for r in rooms if get_display_status(r) != "Full"]
        self._render_room_cards(rooms)

    def _render_room_cards(self, rooms):
        self._rooms_data = rooms
        self._reflow_grid()

    def _reflow_grid(self):
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
        available = self.content_area.width() - 20
        cols = max(1, available // (card_w + spacing))

        for i, room in enumerate(self._rooms_data):
            card = self._create_room_card(room)
            layout.addWidget(card, i // cols, i % cols)

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
        act = QAction("Book Room", self)
        act.triggered.connect(lambda: self._open_booking_dialog(room))
        menu.addAction(act)
        menu.exec(global_pos)

    def _apply_filter(self, status):
        self._current_filter = status
        self._load_rooms()

    def _on_search(self):
        self._load_rooms()

    # ── Booking dialog ───────────────────────────────────

    def _open_booking_dialog(self, preselect_room=None):
        available = [r for r in get_all_rooms() if r["status"] == "Available"]
        if not available:
            QMessageBox.information(self, "Thông báo", "No available rooms.")
            return

        # Load dialog from .ui file
        dlg = QDialog(self)
        uic.loadUi(os.path.join(UI_DIR, "BookingDialog.ui"), dlg)

        # Populate room combo
        for r in available:
            dlg.comboRoom.addItem(
                f"{r['room_id']} – {r['room_type']} ({r['capacity']} Seats)",
                r["id"],
            )

        # Pre-select room nếu được truyền vào
        if preselect_room:
            for i in range(dlg.comboRoom.count()):
                if dlg.comboRoom.itemData(i) == preselect_room["id"]:
                    dlg.comboRoom.setCurrentIndex(i)
                    break

        # Session multi-select toggle logic
        session_buttons = [dlg.btnCa1, dlg.btnCa2, dlg.btnCa3, dlg.btnCa4]
        selected_sessions = set()

        btn_normal = (
            "QPushButton { background: #F5F7FA; border: 2px solid #E3EAF2;"
            " border-radius: 8px; padding: 8px 6px; color: #555; font-size: 12px; font-weight: 500; }"
            " QPushButton:hover { border-color: #1F4F82; background: #EBF0F7; }"
        )
        btn_selected = (
            "QPushButton { background: #1F4F82; border: 2px solid #1F4F82;"
            " border-radius: 8px; padding: 8px 6px; color: white; font-size: 12px; font-weight: 500; }"
        )
        btn_disabled = (
            "QPushButton { background: #EEEEEE; border: 2px solid #BDBDBD;"
            " border-radius: 8px; padding: 8px 6px; color: #BDBDBD; font-size: 12px; font-weight: 500; }"
        )

        for btn in session_buttons:
            btn.setFixedHeight(50)
            btn.setFlat(True)
            btn.setStyleSheet(btn_normal)
            btn.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)

        def get_booked_sessions(room_pk):
            bookings = get_bookings_by_room(room_pk)
            booked = set()
            for b in bookings:
                for idx, (name, time) in enumerate(SESSIONS):
                    if b["session"] == f"{name} ({time})":
                        booked.add(idx)
            return booked

        def refresh_session_buttons():
            room_pk = dlg.comboRoom.currentData()
            booked = get_booked_sessions(room_pk)
            # Xóa các session đã book khỏi selected
            selected_sessions.difference_update(booked)
            for j, b in enumerate(session_buttons):
                if j in booked:
                    b.setEnabled(False)
                    b.setStyleSheet(btn_disabled)
                    b.setToolTip("This session is already booked")
                else:
                    b.setEnabled(True)
                    b.setStyleSheet(btn_selected if j in selected_sessions else btn_normal)
                    b.setToolTip("")

        def on_session_click(idx):
            if idx in selected_sessions:
                selected_sessions.discard(idx)
            else:
                selected_sessions.add(idx)
            for j, b in enumerate(session_buttons):
                if b.isEnabled():
                    b.setStyleSheet(btn_selected if j in selected_sessions else btn_normal)

        for i, btn in enumerate(session_buttons):
            btn.clicked.connect(lambda _, idx=i: on_session_click(idx))

        dlg.comboRoom.currentIndexChanged.connect(lambda _: refresh_session_buttons())
        refresh_session_buttons()

        # Connect action buttons
        dlg.btnCancel.clicked.connect(dlg.reject)
        dlg.btnSubmit.clicked.connect(dlg.accept)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            room_pk = dlg.comboRoom.currentData()
            if not selected_sessions:
                QMessageBox.warning(self, "Lỗi", "Please select at least one session.")
                return
            reason = dlg.txtReason.toPlainText().strip()
            if not reason:
                QMessageBox.warning(self, "Lỗi", "Please enter a reason.")
                return

            success_count = 0
            for idx in sorted(selected_sessions):
                session_name, session_time = SESSIONS[idx]
                session = f"{session_name} ({session_time})"
                if create_booking(self.current_user["id"], room_pk, session, reason):
                    success_count += 1

            if success_count > 0:
                QMessageBox.information(
                    self, "Success",
                    f"Successfully sent booking requests for {success_count} sessions.",
                )
                self._load_rooms()
            else:
                QMessageBox.warning(self, "Error", "Failed to book room.")

    # ── Booking history ──────────────────────────────────

    def _show_history(self):
        dlg = QDialog(self)
        uic.loadUi(os.path.join(UI_DIR, "BookingHistory.ui"), dlg)
        dlg.tableHistory.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        dlg.btnClose.clicked.connect(dlg.accept)
        dlg.comboFilter.currentTextChanged.connect(
            lambda f: self._populate_history(dlg, f)
        )
        self._populate_history(dlg, "All Status")
        dlg.exec()

    def _populate_history(self, dlg, filter_text):
        bookings = get_bookings_by_user(self.current_user["id"])
        if filter_text != "All Status":
            bookings = [b for b in bookings if b["status"] == filter_text]

        table = dlg.tableHistory
        table.setRowCount(len(bookings))
        for row, b in enumerate(bookings):
            table.setItem(row, 0, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 2, QTableWidgetItem(b["session"]))
            table.setItem(row, 3, QTableWidgetItem(b["reason"]))
            table.setItem(row, 4, QTableWidgetItem(b["status"]))
            table.setItem(row, 5, QTableWidgetItem(b.get("locker_password") or ""))
            table.setCellWidget(row, 6, None)
            if b["status"] == "Pending":
                btn_cancel = QPushButton("Cancel")
                btn_cancel.setStyleSheet(
                    "background:#C62828;color:white;border-radius:4px;padding:4px;"
                )
                btn_cancel.clicked.connect(
                    lambda _, bid=b["id"]: self._cancel_booking(bid, dlg)
                )
                table.setCellWidget(row, 6, btn_cancel)

        dlg.lblCount.setText(f"{len(bookings)} bookings")

    def _cancel_booking(self, booking_id, dlg):
        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to cancel this booking?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            cancel_booking(booking_id)
            self._populate_history(dlg, dlg.comboFilter.currentText())
            self._load_rooms()
