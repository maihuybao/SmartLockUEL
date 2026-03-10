from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QDialog, QFileDialog,
    QTableWidgetItem, QPushButton, QHeaderView,
    QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox, QLabel, QWidget,
    QDateEdit, QTimeEdit,
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor

from widgets.base_window import BaseWindow
from models.booking_model import (
    get_all_bookings, delete_booking, admin_update_booking, create_booking,
    approve_booking, reject_booking,
)
from models.room_model import get_all_rooms


def _parse_session(session):
    """Parse 'YYYY-MM-DD | HH:mm - HH:mm' into (date, start, end)."""
    if " | " in session:
        date_part, time_part = session.split(" | ", 1)
        if " - " in time_part:
            start, end = time_part.split(" - ", 1)
            return date_part.strip(), start.strip(), end.strip()
        return date_part.strip(), time_part.strip(), ""
    return "", session, ""


class BookingOverviewController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Booking Overview",
        )
        self.ui = self.load_content_ui("BookingOverview.ui")
        self._current_bookings = []
        self._selected_booking_id = None
        self._connect_signals()
        self._load_table()

    def _connect_sidebar(self):
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(lambda: None)
        self.sidebar.pushButtonEdit.clicked.connect(self._go_edit)
        self.sidebar.pushButtonUsers.clicked.connect(self._go_users)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        self.ui.pushButtonAll.clicked.connect(self._load_table)
        self.ui.pushButtonPending.clicked.connect(self._load_table)
        self.ui.pushButtonApproved.clicked.connect(self._load_table)
        self.ui.pushButtonRejected.clicked.connect(self._load_table)
        self.ui.lineEditSearch.textChanged.connect(self._load_table)
        self.ui.pushButtonAdd.clicked.connect(self._add_booking)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)
        self.ui.tableWidgetBookings.cellClicked.connect(self._on_row_click)
        self.ui.pushButtonApprove.clicked.connect(self._approve_booking)
        self.ui.pushButtonReject.clicked.connect(self._reject_booking)

    # -- Table ----------------------------------------------------

    def _load_table(self):
        bookings = get_all_bookings()

        if self.ui.pushButtonPending.isChecked():
            status_filter = "Pending"
        elif self.ui.pushButtonApproved.isChecked():
            status_filter = "Approved"
        elif self.ui.pushButtonRejected.isChecked():
            status_filter = "Rejected"
        else:
            status_filter = "All Status"

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
        self._current_bookings = bookings
        table = self.ui.tableWidgetBookings
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        table.horizontalHeader().setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(9, 70)
        table.setColumnWidth(10, 70)

        for row, b in enumerate(bookings):
            date, start, end = _parse_session(b.get("session", ""))
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(b["username"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 2, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 3, QTableWidgetItem(date))
            table.setItem(row, 4, QTableWidgetItem(start))
            table.setItem(row, 5, QTableWidgetItem(end))
            table.setItem(row, 6, QTableWidgetItem(b["reason"]))

            status_item = QTableWidgetItem(b["status"])
            status_colors = {"Pending": "#FF9800", "Approved": "#4CAF50", "Rejected": "#F44336"}
            status_item.setForeground(QColor(status_colors.get(b["status"], "#333")))
            table.setItem(row, 7, status_item)
            table.setItem(row, 8, QTableWidgetItem(b.get("locker_password") or ""))

            table.setCellWidget(row, 9, self._make_btn("Edit", "#1F4F82", "#163D66", lambda _, bid=b["id"]: self._edit_booking(bid)))
            table.setCellWidget(row, 10, self._make_btn("Delete", "#F44336", "#C62828", lambda _, bid=b["id"]: self._delete_booking(bid)))

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

    def _on_row_click(self, row, _col):
        if row >= len(self._current_bookings):
            return
        b = self._current_bookings[row]
        self._selected_booking_id = b["id"]
        date, start, end = _parse_session(b.get("session", ""))
        self.ui.lineEditNumber.setText(str(b["id"]))
        self.ui.lineEditDate.setText(date)
        self.ui.lineEditFullName.setText(b["username"])
        self.ui.lineEditStartTime.setText(start)
        self.ui.lineEditNameID.setText(str(b.get("user_id", "")))
        self.ui.lineEditEndTime.setText(end)
        self.ui.lineEditRoom.setText(b["room_name"])
        self.ui.lineEditPurpose.setText(b.get("reason", ""))

    def _approve_booking(self):
        if not self._selected_booking_id:
            QMessageBox.warning(self, "Error", "Please select a booking first.")
            return
        password = approve_booking(self._selected_booking_id)
        QMessageBox.information(
            self, "Approved",
            f"Booking approved.\nLocker password: {password}",
        )
        self._selected_booking_id = None
        self._load_table()

    def _reject_booking(self):
        if not self._selected_booking_id:
            QMessageBox.warning(self, "Error", "Please select a booking first.")
            return
        reject_note = self.ui.txtRejectReason.toPlainText().strip()
        if not reject_note:
            QMessageBox.warning(self, "Error", "Please enter a rejection reason.")
            return
        reject_booking(self._selected_booking_id, reject_note)
        self._selected_booking_id = None
        self.ui.txtRejectReason.clear()
        self._load_table()

    # -- Actions --------------------------------------------------

    def _add_booking(self):
        dlg = self._build_booking_dialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            user_id = dlg.comboUser.currentData()
            room_id = dlg.comboRoom.currentData()
            date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
            start_str = dlg.timeEditStart.time().toString("HH:mm")
            end_str = dlg.timeEditEnd.time().toString("HH:mm")
            session = f"{date_str} | {start_str} - {end_str}"
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
            date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
            start_str = dlg.timeEditStart.time().toString("HH:mm")
            end_str = dlg.timeEditEnd.time().toString("HH:mm")
            session = f"{date_str} | {start_str} - {end_str}"
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
        if self.ui.pushButtonPending.isChecked():
            bookings = [b for b in bookings if b["status"] == "Pending"]
        elif self.ui.pushButtonApproved.isChecked():
            bookings = [b for b in bookings if b["status"] == "Approved"]
        elif self.ui.pushButtonRejected.isChecked():
            bookings = [b for b in bookings if b["status"] == "Rejected"]
        keyword = self.ui.lineEditSearch.text().strip().lower()
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
                writer.writerow(["User", "Room", "Type", "Date", "Start Time", "End Time", "Purpose", "Status", "Locker Password"])
                for b in bookings:
                    date, start, end = _parse_session(b.get("session", ""))
                    writer.writerow([
                        b["username"],
                        b["room_name"],
                        b["room_type"],
                        date, start, end,
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
        dlg.setMinimumWidth(420)
        dlg.setStyleSheet(
            "QDialog { background: white; }"
            "QLabel { color: #333; font-size: 13px; }"
            "QComboBox, QLineEdit, QDateEdit, QTimeEdit { padding: 6px; border: 1px solid #ddd; border-radius: 6px; color: #333; font-size: 13px; background: white; }"
            "QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus { border: 1px solid #1F4F82; }"
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
            combo_room.addItem(f"{r['room_id']} - {r['room_type']}", r["id"])
        dlg.comboRoom = combo_room

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.setDate(QDate.currentDate())
        dlg.dateEdit = date_edit

        time_start = QTimeEdit()
        time_start.setDisplayFormat("HH:mm")
        time_start.setTime(QTime(7, 0))
        dlg.timeEditStart = time_start

        time_end = QTimeEdit()
        time_end.setDisplayFormat("HH:mm")
        time_end.setTime(QTime(9, 0))
        dlg.timeEditEnd = time_end

        edit_reason = QLineEdit()
        edit_reason.setPlaceholderText("Enter purpose...")
        dlg.editReason = edit_reason

        form.addRow("User:", combo_user)
        form.addRow("Room:", combo_room)
        form.addRow("Date:", date_edit)
        form.addRow("Start Time:", time_start)
        form.addRow("End Time:", time_end)
        form.addRow("Purpose:", edit_reason)

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

            # Parse existing session
            session = booking.get("session", "")
            if " | " in session:
                date_part, time_part = session.split(" | ", 1)
                parsed_date = QDate.fromString(date_part, "yyyy-MM-dd")
                if parsed_date.isValid():
                    date_edit.setDate(parsed_date)
                if " - " in time_part:
                    s_str, e_str = time_part.split(" - ", 1)
                    parsed_start = QTime.fromString(s_str.strip(), "HH:mm")
                    parsed_end = QTime.fromString(e_str.strip(), "HH:mm")
                    if parsed_start.isValid():
                        time_start.setTime(parsed_start)
                    if parsed_end.isValid():
                        time_end.setTime(parsed_end)

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
