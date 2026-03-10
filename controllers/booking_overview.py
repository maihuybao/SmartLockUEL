from PyQt6.QtWidgets import (
    QApplication,
    QMessageBox,
    QDialog,
    QFileDialog,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QLabel,
    QWidget,
    QDateEdit,
    QTimeEdit,
)
from PyQt6.QtCore import Qt, QDate, QTime, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def _svg_icon(name, color, size=16):
    import re

    path = os.path.join(IMAGES_DIR, name)
    if not os.path.exists(path):
        return QIcon()
    with open(path, "r", encoding="utf-8") as f:
        svg = f.read()
    svg = re.sub(r'fill="#[0-9a-fA-F]+"', f'fill="{color}"', svg)
    svg = re.sub(r"fill='#[0-9a-fA-F]+'", f"fill='{color}'", svg)
    if f'fill="{color}"' not in svg:
        svg = svg.replace("<path ", f'<path fill="{color}" ', 1)
    renderer = QSvgRenderer(svg.encode("utf-8"))
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)


from widgets.base_window import BaseWindow
from models.booking_model import (
    get_all_bookings,
    delete_booking,
    admin_update_booking,
    create_booking,
    approve_booking,
    reject_booking,
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
            user,
            role_text="Admin",
            show_search=False,
            show_sidebar=True,
            title="SmartLocker UEL - Booking Management",
        )
        self.ui = self.load_content_ui("BookingManagement.ui")
        self._current_bookings = []
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
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

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
                b
                for b in bookings
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
        table.setColumnWidth(9, 130)
        table.verticalHeader().setDefaultSectionSize(32)

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
            status_colors = {
                "Pending": "#FF9800",
                "Approved": "#4CAF50",
                "Rejected": "#F44336",
            }
            status_item.setForeground(QColor(status_colors.get(b["status"], "#333")))
            table.setItem(row, 7, status_item)
            table.setItem(row, 8, QTableWidgetItem(b.get("locker_password") or ""))

            table.setCellWidget(row, 9, self._make_actions_widget(b["id"], b["status"]))

    def _make_icon_btn(self, icon_file, tooltip, icon_color, bg, hover, slot):
        btn = QPushButton()
        btn.setToolTip(tooltip)
        btn.setFixedSize(22, 22)
        btn.setIcon(_svg_icon(icon_file, icon_color))
        btn.setIconSize(QSize(14, 14))
        btn.setStyleSheet(
            f"QPushButton{{background:{bg};border:none;border-radius:5px;}}"
            f"QPushButton:hover{{background:{hover};}}"
        )
        btn.clicked.connect(slot)
        return btn

    def _make_actions_widget(self, booking_id, status):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.addWidget(
            self._make_icon_btn(
                "view.svg",
                "View",
                "#6A1B9A",
                "#F3E5F5",
                "#E1BEE7",
                lambda _, bid=booking_id: self._view_booking(bid),
            )
        )
        if status == "Pending":
            layout.addWidget(
                self._make_icon_btn(
                    "approve.svg",
                    "Approve",
                    "#2E7D32",
                    "#E8F5E9",
                    "#C8E6C9",
                    lambda _, bid=booking_id: self._approve_booking_inline(bid),
                )
            )
            layout.addWidget(
                self._make_icon_btn(
                    "reject.svg",
                    "Reject",
                    "#E65100",
                    "#FFF3E0",
                    "#FFE0B2",
                    lambda _, bid=booking_id: self._reject_booking_inline(bid),
                )
            )
        layout.addWidget(
            self._make_icon_btn(
                "edit.svg",
                "Edit",
                "#1565C0",
                "#E3F2FD",
                "#BBDEFB",
                lambda _, bid=booking_id: self._edit_booking(bid),
            )
        )
        layout.addWidget(
            self._make_icon_btn(
                "delete.svg",
                "Delete",
                "#C62828",
                "#FFEBEE",
                "#FFCDD2",
                lambda _, bid=booking_id: self._delete_booking(bid),
            )
        )
        layout.addStretch()
        return container

    def _view_booking(self, booking_id):
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return

        date, start, end = _parse_session(b.get("session", ""))

        status_colors = {"Pending": "#FF9800", "Approved": "#4CAF50", "Rejected": "#F44336"}
        status_color = status_colors.get(b["status"], "#333")

        dlg = QDialog(self)
        dlg.setWindowTitle("Booking Details")
        dlg.setMinimumWidth(420)
        dlg.setStyleSheet("QDialog { background: white; }")

        layout = QVBoxLayout(dlg)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 20)

        # Header strip
        header = QLabel(f"Booking #{b['id']}")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "QLabel { background: #1F4F82; color: white; font-size: 16px;"
            " font-weight: bold; padding: 16px; }"
        )
        layout.addWidget(header)

        # Status badge
        badge = QLabel(b["status"])
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"QLabel {{ background: {status_color}; color: white; font-size: 12px;"
            f" font-weight: bold; padding: 4px 0; }}"
        )
        layout.addWidget(badge)

        # Fields
        body = QWidget()
        body.setStyleSheet("background: white;")
        form = QFormLayout(body)
        form.setSpacing(10)
        form.setContentsMargins(24, 20, 24, 8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        field_style = (
            "QLineEdit { border: 1px solid #E0E0E0; border-radius: 6px;"
            " padding: 6px 10px; font-size: 13px; color: #333; background: #FAFAFA; }"
        )
        label_style = "color: #1F4F82; font-weight: 600; font-size: 13px;"

        def _row(label, value):
            lbl = QLabel(label)
            lbl.setStyleSheet(label_style)
            val = QLineEdit(str(value) if value else "—")
            val.setReadOnly(True)
            val.setStyleSheet(field_style)
            form.addRow(lbl, val)

        _row("User", b["username"])
        _row("Room", f"{b['room_name']}  ({b['room_type']})")
        _row("Date", date)
        _row("Start Time", start)
        _row("End Time", end)
        _row("Purpose", b.get("reason", ""))
        _row("Locker Password", b.get("locker_password") or "—")
        if b.get("reject_reason"):
            _row("Reject Reason", b["reject_reason"])

        layout.addWidget(body)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(24, 0, 24, 0)
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setFlat(True)
        btn_close.setStyleSheet(
            "QPushButton { background: #1F4F82; border: none; border-radius: 6px;"
            " padding: 8px 28px; color: white; font-size: 13px; font-weight: bold; }"
            "QPushButton:hover { background: #163D66; }"
        )
        btn_close.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        dlg.exec()

    def _approve_booking_inline(self, booking_id):
        password = approve_booking(booking_id)
        QMessageBox.information(
            self, "Approved", f"Booking approved.\nLocker password: {password}"
        )
        self._load_table()

    def _reject_booking_inline(self, booking_id):
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return
        dlg = self._build_booking_dialog(booking=b, reject_mode=True)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            reason = dlg.editRejectReason.text().strip()
            if not reason:
                QMessageBox.warning(self, "Error", "Please enter a rejection reason.")
                return
            reject_booking(booking_id, reason)
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

    def _import_csv(self):
        import csv
        from models.user_model import get_all_users

        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return

        users = {u["username"]: u["id"] for u in get_all_users()}
        rooms = {r["room_id"]: r["id"] for r in get_all_rooms()}
        imported = 0
        skipped = 0
        errors = []

        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):
                    username = (row.get("username") or "").strip()
                    room_id_str = (row.get("room_id") or "").strip()
                    date_str = (row.get("date") or "").strip()
                    start_str = (row.get("start_time") or "").strip()
                    end_str = (row.get("end_time") or "").strip()
                    reason = (row.get("reason") or "").strip()

                    if not all(
                        [username, room_id_str, date_str, start_str, end_str, reason]
                    ):
                        errors.append(f"Row {i}: missing required fields")
                        skipped += 1
                        continue
                    user_pk = users.get(username)
                    if not user_pk:
                        errors.append(f"Row {i}: username '{username}' not found")
                        skipped += 1
                        continue
                    room_pk = rooms.get(room_id_str)
                    if not room_pk:
                        errors.append(f"Row {i}: room_id '{room_id_str}' not found")
                        skipped += 1
                        continue

                    session = f"{date_str} | {start_str} - {end_str}"
                    if create_booking(user_pk, room_pk, session, reason):
                        imported += 1
                    else:
                        errors.append(
                            f"Row {i}: conflict or error for '{username}' in '{room_id_str}'"
                        )
                        skipped += 1
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file:\n{e}")
            return

        self._load_table()
        msg = f"Imported: {imported}  |  Skipped: {skipped}"
        if errors:
            msg += "\n\nDetails:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n... and {len(errors) - 10} more"
        QMessageBox.information(self, "Import Complete", msg)

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
                b
                for b in bookings
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
                writer.writerow(
                    [
                        "User",
                        "Room",
                        "Type",
                        "Date",
                        "Start Time",
                        "End Time",
                        "Purpose",
                        "Status",
                        "Locker Password",
                    ]
                )
                for b in bookings:
                    date, start, end = _parse_session(b.get("session", ""))
                    writer.writerow(
                        [
                            b["username"],
                            b["room_name"],
                            b["room_type"],
                            date,
                            start,
                            end,
                            b["reason"],
                            b["status"],
                            b.get("locker_password") or "",
                        ]
                    )
            QMessageBox.information(
                self, "Export CSV", f"Exported {len(bookings)} bookings successfully."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")

    def _build_booking_dialog(self, booking=None, reject_mode=False):
        from models.user_model import get_all_users

        dlg = QDialog(self)
        if reject_mode:
            dlg.setWindowTitle("Reject Booking")
        else:
            dlg.setWindowTitle("Add Booking" if not booking else "Edit Booking")
        dlg.setMinimumWidth(420)
        dlg.setStyleSheet(
            "QDialog { background: white; }"
            "QLabel { color: #333; font-size: 13px; }"
            "QComboBox, QLineEdit, QDateEdit, QTimeEdit { padding: 6px; border: 1px solid #ddd; border-radius: 6px; color: #333; font-size: 13px; background: white; }"
            "QComboBox:focus, QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus { border: 1px solid #1F4F82; }"
            "QComboBox:disabled, QLineEdit:disabled, QDateEdit:disabled, QTimeEdit:disabled { background: #f5f5f5; color: #999; }"
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
            if not reject_mode:
                form.addRow("Status:", combo_status)

            for i in range(combo_user.count()):
                if combo_user.itemData(i) == booking.get("user_id"):
                    combo_user.setCurrentIndex(i)
                    break
            for i in range(combo_room.count()):
                if combo_room.itemText(i).startswith(booking["room_name"]):
                    combo_room.setCurrentIndex(i)
                    break

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

            if reject_mode:
                combo_user.setEnabled(False)
                combo_room.setEnabled(False)
                date_edit.setEnabled(False)
                time_start.setEnabled(False)
                time_end.setEnabled(False)
                edit_reason.setEnabled(False)
                edit_reject = QLineEdit()
                edit_reject.setPlaceholderText("Enter rejection reason...")
                edit_reject.setText(booking.get("reject_reason") or "")
                dlg.editRejectReason = edit_reject
                form.addRow("Reject Reason:", edit_reject)
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
