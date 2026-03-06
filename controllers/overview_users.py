from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QDialog, QComboBox, QTextEdit, QDialogButtonBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QApplication,
)
from PyQt6.QtCore import Qt

from widgets.base_window import BaseWindow
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import (
    create_booking, get_bookings_by_user, cancel_booking,
)

STATUS_COLORS = {
    "Available": "#4CAF50",
    "Occupied": "#F44336",
    "Booked": "#FF9800",
    "Cleaning": "#2196F3",
}


class OverviewUsersController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="User", show_search=True,
            show_sidebar=False, title="SmartLocker UEL - User",
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
        self.ui.btnBooked.clicked.connect(lambda: self._apply_filter("Booked"))
        self.ui.btnCleaning.clicked.connect(lambda: self._apply_filter("Cleaning"))

        # Search
        self.navbar.lineEditSearch.textChanged.connect(self._on_search)

        # Navbar role button → history
        self.navbar.btnRole.clicked.connect(self._show_history)

        # Bottom bar
        self.ui.btnBooking.clicked.connect(self._open_booking_dialog)
        self.ui.btnLogout.clicked.connect(self._logout)
        self.ui.btnQuit.clicked.connect(QApplication.quit)

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
        layout = self.ui.gridLayout
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        cols = 3
        for i, room in enumerate(rooms):
            card = self._create_room_card(room)
            layout.addWidget(card, i // cols, i % cols)

    def _create_room_card(self, room):
        color = STATUS_COLORS.get(room["status"], "#9E9E9E")
        card = QWidget()
        card.setFixedSize(180, 120)
        card.setStyleSheet(
            f"background-color: white; border: 2px solid {color};"
            f"border-radius: 10px;"
        )
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(10, 8, 10, 8)

        lbl_id = QLabel(room["room_id"])
        lbl_id.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        lbl_type = QLabel(room["room_type"])
        lbl_type.setStyleSheet("color: #666; font-size: 11px; border: none;")
        lbl_cap = QLabel(f"Sức chứa: {room['capacity']}")
        lbl_cap.setStyleSheet("color: #666; font-size: 11px; border: none;")
        lbl_status = QLabel(room["status"])
        lbl_status.setStyleSheet(
            f"color: white; background-color: {color};"
            f"border-radius: 8px; padding: 2px 8px; font-size: 11px;"
        )
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(lbl_id)
        vbox.addWidget(lbl_type)
        vbox.addWidget(lbl_cap)
        vbox.addWidget(lbl_status)
        return card

    def _apply_filter(self, status):
        self._current_filter = status
        self._load_rooms()

    def _on_search(self):
        self._load_rooms()

    # ── Booking dialog ───────────────────────────────────

    def _open_booking_dialog(self):
        available = [r for r in get_all_rooms() if r["status"] == "Available"]
        if not available:
            QMessageBox.information(self, "Thông báo", "Không có phòng trống.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Đặt phòng")
        dlg.setMinimumWidth(350)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel("Chọn phòng:"))
        combo_room = QComboBox()
        for r in available:
            combo_room.addItem(
                f"{r['room_id']} - {r['room_type']} ({r['capacity']} chỗ)", r["id"],
            )
        layout.addWidget(combo_room)

        layout.addWidget(QLabel("Buổi:"))
        combo_session = QComboBox()
        combo_session.addItems(["Sang", "Chieu", "Toi"])
        layout.addWidget(combo_session)

        layout.addWidget(QLabel("Lý do:"))
        txt_reason = QTextEdit()
        txt_reason.setPlaceholderText("Họp nhóm, sinh hoạt CLB, tự học, dạy bù, hội thảo, báo cáo luận văn...")
        txt_reason.setMaximumHeight(80)
        layout.addWidget(txt_reason)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            room_pk = combo_room.currentData()
            session = combo_session.currentText()
            reason = txt_reason.toPlainText().strip()
            if not reason:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập lý do.")
                return
            if create_booking(self.current_user["id"], room_pk, session, reason):
                QMessageBox.information(self, "Thành công", "Đã gửi yêu cầu đặt phòng.")
                self._load_rooms()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể đặt phòng.")

    # ── Booking history ──────────────────────────────────

    def _show_history(self):
        bookings = get_bookings_by_user(self.current_user["id"])
        dlg = QDialog(self)
        dlg.setWindowTitle("Lịch sử đặt phòng")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)

        table = QTableWidget(len(bookings), 7)
        table.setHorizontalHeaderLabels(
            ["Phòng", "Loại", "Buổi", "Lý do", "Trạng thái", "Mật khẩu tủ", ""]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, b in enumerate(bookings):
            table.setItem(row, 0, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 2, QTableWidgetItem(b["session"]))
            table.setItem(row, 3, QTableWidgetItem(b["reason"]))
            table.setItem(row, 4, QTableWidgetItem(b["status"]))
            table.setItem(row, 5, QTableWidgetItem(b.get("locker_password") or ""))

            if b["status"] == "Pending":
                btn_cancel = QPushButton("Hủy")
                btn_cancel.setStyleSheet("background:#C62828;color:white;border-radius:4px;padding:4px;")
                btn_cancel.clicked.connect(lambda _, bid=b["id"]: self._cancel_booking(bid, dlg))
                table.setCellWidget(row, 6, btn_cancel)

        layout.addWidget(table)
        dlg.exec()

    def _cancel_booking(self, booking_id, dlg):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn hủy lịch đặt này?")
        if reply == QMessageBox.StandardButton.Yes:
            cancel_booking(booking_id)
            dlg.close()
            self._show_history()
            self._load_rooms()
