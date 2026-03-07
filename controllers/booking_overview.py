from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QDialog, QFileDialog,
    QTableWidgetItem, QPushButton, QHeaderView,
    QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel, QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from widgets.base_window import BaseWindow
from models.booking_model import (
    get_all_bookings, delete_booking, admin_update_booking, create_booking,
)
from models.room_model import get_all_rooms
from widgets.room_card import SESSIONS


class BookingOverviewController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Booking Overview",
        )
        self.ui = self.load_content_ui("BookingOverview.ui")
        self._connect_sidebar_override()
        self._connect_signals()
        self._load_table()

    def _connect_sidebar(self):
        self.sidebar.btnOverview.clicked.connect(self._go_overview)
        self.sidebar.btnBookings.clicked.connect(lambda: None)
        self.sidebar.btnEdit.clicked.connect(self._go_edit)
        self.sidebar.btnUsers.clicked.connect(self._go_users)
        self.sidebar.btnLogout.clicked.connect(self._logout)
        self.sidebar.btnQuit.clicked.connect(self._quit)

    def _connect_sidebar_override(self):
        pass

    def _connect_signals(self):
        self.ui.comboFilter.currentTextChanged.connect(self._load_table)
        self.ui.lineEditSearch.textChanged.connect(self._load_table)
        self.ui.btnAdd.clicked.connect(self._add_booking)
        self.ui.btnExportCSV.clicked.connect(self._export_csv)

    # ── Table ────────────────────────────────────────────

    def _load_table(self):
        bookings = get_all_bookings()
        status_filter = self.ui.comboFilter.currentText()
        keyword = self.ui.lineEditSearch.text().strip().lower()

        if status_filter != "All Status":
            bookings = [b for b in bookings if b["status"] == status_filter]
        if keyword:
            bookings = [
                b for b in bookings
                if keyword in b["username"].lower()
                or keyword in b["room_name"].lower()
                or keyword in b["session"].lower()
            ]

        self.ui.lblCount.setText(f"{len(bookings)} bookings")
        table = self.ui.tableBookings
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(7, 70)
        table.setColumnWidth(8, 70)

        for row, b in enumerate(bookings):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(b["username"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 2, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 3, QTableWidgetItem(b["session"]))
            table.setItem(row, 4, QTableWidgetItem(b["reason"]))

            status_item = QTableWidgetItem(b["status"])
            status_colors = {"Pending": "#FF9800", "Approved": "#4CAF50", "Rejected": "#F44336"}
            status_item.setForeground(QColor(status_colors.get(b["status"], "#333")))
            table.setItem(row, 5, status_item)
            table.setItem(row, 6, QTableWidgetItem(b.get("locker_password") or ""))

            table.setCellWidget(row, 7, self._make_btn("Edit", "#1F4F82", "#163D66", lambda _, bid=b["id"]: self._edit_booking(bid)))
            table.setCellWidget(row, 8, self._make_btn("Delete", "#F44336", "#C62828", lambda _, bid=b["id"]: self._delete_booking(bid)))

    def _make_btn(self, text, bg, hover, slot):
        btn = QPushButton(text)
        btn.setFlat(True)
        btn.setStyleSheet(
            f"QPushButton{{background:{bg};color:white;border:none;"
            f"font-size:11px;font-family:Arial;padding:2px 6px;}}"
            f"QPushButton:hover{{background:{hover};}}"
        )
        btn.clicked.connect(slot)
        return btn

    # ── Actions ──────────────────────────────────────────

    def _add_booking(self):
        dlg = self._build_booking_dialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            user_id = dlg.comboUser.currentData()
            room_id = dlg.comboRoom.currentData()
            session = dlg.comboSession.currentText()
            reason = dlg.editReason.text().strip()
            if not reason:
                QMessageBox.warning(self, "Error", "Please enter a reason.")
                return
            if create_booking(user_id, room_id, session, reason):
                self._load_table()
            else:
                QMessageBox.warning(self, "Error", "Failed to create booking.")

    def _edit_booking(self, booking_id):
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return
        dlg = self._build_booking_dialog(booking=b)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            session = dlg.comboSession.currentText()
            reason = dlg.editReason.text().strip()
            status = dlg.comboStatus.currentText()
            if not reason:
                QMessageBox.warning(self, "Error", "Please enter a reason.")
                return
            admin_update_booking(booking_id, session, reason, status)
            self._load_table()

    def _delete_booking(self, booking_id):
        reply = QMessageBox.question(self, "Confirm", "Delete this booking?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_booking(booking_id)
            self._load_table()

    def _export_csv(self):
        import csv
        bookings = get_all_bookings()
        status_filter = self.ui.comboFilter.currentText()
        keyword = self.ui.lineEditSearch.text().strip().lower()
        if status_filter != "All Status":
            bookings = [b for b in bookings if b["status"] == status_filter]
        if keyword:
            bookings = [
                b for b in bookings
                if keyword in b["username"].lower()
                or keyword in b["room_name"].lower()
                or keyword in b["session"].lower()
            ]

        if not bookings:
            QMessageBox.information(self, "Export CSV", "No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "bookings.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["User", "Room", "Type", "Session", "Reason", "Status", "Locker Password"])
                for b in bookings:
                    writer.writerow([
                        b["username"],
                        b["room_name"],
                        b["room_type"],
                        b["session"],
                        b["reason"],
                        b["status"],
                        b.get("locker_password") or "",
                    ])
            QMessageBox.information(self, "Export CSV", f"Exported {len(bookings)} bookings successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")

    def _build_booking_dialog(self, booking=None):
        from models.user_model import get_all_users
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Booking" if not booking else "Edit Booking")
        dlg.setMinimumWidth(400)
        dlg.setStyleSheet(
            "QDialog { background: white; }"
            "QLabel { color: #333; font-size: 13px; }"
            "QComboBox, QLineEdit { padding: 6px; border: 1px solid #ddd; border-radius: 6px; color: #333; font-size: 13px; background: white; }"
            "QComboBox:focus, QLineEdit:focus { border: 1px solid #1F4F82; }"
        )

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        combo_user = QComboBox()
        users = get_all_users()
        for u in users:
            combo_user.addItem(u["username"], u["id"])
        dlg.comboUser = combo_user

        combo_room = QComboBox()
        rooms = get_all_rooms()
        for r in rooms:
            combo_room.addItem(f"{r['room_id']} – {r['room_type']}", r["id"])
        dlg.comboRoom = combo_room

        combo_session = QComboBox()
        for name, tr in SESSIONS:
            combo_session.addItem(f"{name} ({tr})")
        dlg.comboSession = combo_session

        edit_reason = QLineEdit()
        edit_reason.setPlaceholderText("Enter reason...")
        dlg.editReason = edit_reason

        form.addRow("User:", combo_user)
        form.addRow("Room:", combo_room)
        form.addRow("Session:", combo_session)
        form.addRow("Reason:", edit_reason)

        if booking:
            combo_status = QComboBox()
            for s in ("Pending", "Approved", "Rejected"):
                combo_status.addItem(s)
            combo_status.setCurrentText(booking["status"])
            dlg.comboStatus = combo_status
            form.addRow("Status:", combo_status)

            for i in range(combo_user.count()):
                if combo_user.itemData(i) == booking.get("user_id"):
                    combo_user.setCurrentIndex(i)
                    break
            for i in range(combo_room.count()):
                if combo_room.itemText(i).startswith(booking["room_name"]):
                    combo_room.setCurrentIndex(i)
                    break
            for i in range(combo_session.count()):
                if combo_session.itemText(i) == booking["session"]:
                    combo_session.setCurrentIndex(i)
                    break
            edit_reason.setText(booking["reason"])
        else:
            dlg.comboStatus = None

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFlat(True)
        btn_cancel.setStyleSheet(
            "QPushButton{background:#F5F5F5;border:1px solid #ddd;border-radius:6px;padding:7px 20px;color:#555;font-size:13px;}"
            "QPushButton:hover{background:#E0E0E0;}"
        )
        btn_ok = QPushButton("Save")
        btn_ok.setFlat(True)
        btn_ok.setStyleSheet(
            "QPushButton{background:#1F4F82;border:none;border-radius:6px;padding:7px 20px;color:white;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#163D66;}"
        )
        btn_cancel.clicked.connect(dlg.reject)
        btn_ok.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        return dlg
