from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QApplication, QMessageBox, QDialog, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView, QInputDialog,
)
from PyQt6.QtCore import Qt

from widgets.base_window import BaseWindow
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import get_all_bookings, approve_booking, reject_booking, get_dashboard_stats

STATUS_COLORS = {
    "Available": "#4CAF50",
    "Occupied": "#F44336",
    "Booked": "#FF9800",
    "Cleaning": "#2196F3",
}


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
        self.ui.btnBooked.clicked.connect(lambda: self._apply_filter("Booked"))
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

    # ── Booking Management ───────────────────────────────

    def _show_booking_management(self):
        bookings = get_all_bookings()
        stats = get_dashboard_stats()

        dlg = QDialog(self)
        dlg.setWindowTitle("Quản lý lịch đặt phòng")
        dlg.setMinimumSize(750, 500)
        layout = QVBoxLayout(dlg)

        stats_layout = QHBoxLayout()
        for label, value, color in [
            ("Tổng phòng", stats["total_rooms"], "#1565C0"),
            ("Tổng booking", stats["total_bookings"], "#FF9800"),
            ("Chờ duyệt", stats["pending"], "#9C27B0"),
            ("Đã duyệt", stats["approved"], "#4CAF50"),
            ("Từ chối", stats["rejected"], "#F44336"),
        ]:
            card = QLabel(f"{label}\n{value}")
            card.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card.setStyleSheet(
                f"background-color:{color};color:white;border-radius:8px;"
                f"padding:10px;font-size:13px;font-weight:bold;"
            )
            card.setFixedHeight(60)
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        table = QTableWidget(len(bookings), 8)
        table.setHorizontalHeaderLabels(
            ["User", "Phòng", "Loại", "Buổi", "Lý do", "Trạng thái", "", ""]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for row, b in enumerate(bookings):
            table.setItem(row, 0, QTableWidgetItem(b["username"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 2, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 3, QTableWidgetItem(b["session"]))
            table.setItem(row, 4, QTableWidgetItem(b["reason"]))
            table.setItem(row, 5, QTableWidgetItem(b["status"]))

            if b["status"] == "Pending":
                btn_approve = QPushButton("Duyệt")
                btn_approve.setStyleSheet(
                    "background:#4CAF50;color:white;border-radius:4px;padding:4px;"
                )
                btn_approve.clicked.connect(
                    lambda _, bid=b["id"]: self._approve(bid, dlg)
                )
                table.setCellWidget(row, 6, btn_approve)

                btn_reject = QPushButton("Từ chối")
                btn_reject.setStyleSheet(
                    "background:#F44336;color:white;border-radius:4px;padding:4px;"
                )
                btn_reject.clicked.connect(
                    lambda _, bid=b["id"]: self._reject(bid, dlg)
                )
                table.setCellWidget(row, 7, btn_reject)

        layout.addWidget(table)
        dlg.exec()

    def _approve(self, booking_id, dlg):
        password = approve_booking(booking_id)
        QMessageBox.information(
            self, "Đã duyệt",
            f"Booking đã được duyệt.\nMật khẩu tủ thiết bị: {password}",
        )
        dlg.close()
        self._show_booking_management()
        self._load_rooms()

    def _reject(self, booking_id, dlg):
        reason, ok = QInputDialog.getText(
            self, "Từ chối", "Nhập lý do từ chối:"
        )
        if ok and reason.strip():
            reject_booking(booking_id, reason.strip())
            QMessageBox.information(self, "Đã từ chối", "Booking đã bị từ chối.")
            dlg.close()
            self._show_booking_management()
            self._load_rooms()
