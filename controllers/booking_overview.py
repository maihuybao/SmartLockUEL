from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QDialog,
    QFileDialog,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QDate, QTime, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6 import uic
import os
from paths import resource_dir

BASE_DIR = resource_dir()
IMAGES_DIR = os.path.join(BASE_DIR, "images")
UI_DIR = os.path.join(BASE_DIR, "ui")


def _png_icon(name):
    """Load a PNG icon from the images directory.

    Args:
        name (str): The filename of the icon (e.g., 'edit.png').

    Returns:
        QIcon: The loaded icon, or an empty QIcon if the file does not exist.
    """
    path = os.path.join(IMAGES_DIR, name)
    if not os.path.exists(path):
        return QIcon()
    return QIcon(path)


from models.booking_model import (
    get_all_bookings,
    delete_booking,
    admin_update_booking,
    create_booking,
    approve_booking,
    reject_booking,
)
from models.room_model import get_all_rooms


class BookingOverviewPage(QWidget):
    """Admin page for managing all bookings with filtering, search, and CRUD operations.

    Provides a table view of bookings with inline actions for viewing,
    approving, rejecting, editing, and deleting. Supports CSV import/export.

    Args:
        shell (AdminShellController): The parent admin shell controller.
    """

    def __init__(self, shell):
        """Initialize the booking management page, load UI, and display bookings."""
        super().__init__()
        self._shell = shell
        self._current_bookings = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.ui = QWidget()
        uic.loadUi(os.path.join(UI_DIR, "BookingManagement.ui"), self.ui)
        layout.addWidget(self.ui)

        self._connect_signals()
        self._load_table()

    def _connect_signals(self):
        """Connect filter buttons, search field, and action buttons to handlers."""
        self.ui.pushButtonAll.clicked.connect(self._load_table)
        self.ui.pushButtonPending.clicked.connect(self._load_table)
        self.ui.pushButtonApproved.clicked.connect(self._load_table)
        self.ui.pushButtonRejected.clicked.connect(self._load_table)
        self.ui.lineEditSearch.textChanged.connect(self._load_table)
        self.ui.pushButtonAdd.clicked.connect(self._add_booking)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    def refresh(self):
        """Reload the bookings table data from the database."""
        self._load_table()

    # -- Table ----------------------------------------------------

    def _load_table(self):
        """Load and display bookings in the table, applying status and search filters."""
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
                or keyword in b.get("date", "").lower()
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
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(b["username"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 2, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 3, QTableWidgetItem(b.get("date", "")))
            table.setItem(row, 4, QTableWidgetItem(b.get("time_start", "")))
            table.setItem(row, 5, QTableWidgetItem(b.get("time_end", "")))
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

    def _make_icon_btn(self, icon_file, tooltip, bg, hover, slot):
        """Create a small icon button with custom styling for table action cells.

        Args:
            icon_file (str): The icon filename in the images directory.
            tooltip (str): The tooltip text for the button.
            bg (str): The CSS background color for the button.
            hover (str): The CSS background color on hover.
            slot (callable): The callback function to connect to the click signal.

        Returns:
            QPushButton: The configured icon button.
        """
        btn = QPushButton()
        btn.setToolTip(tooltip)
        btn.setFixedSize(22, 22)
        btn.setIcon(_png_icon(icon_file))
        btn.setIconSize(QSize(14, 14))
        btn.setStyleSheet(
            f"QPushButton{{background:{bg};border:none;border-radius:5px;}}"
            f"QPushButton:hover{{background:{hover};}}"
        )
        btn.clicked.connect(slot)
        return btn

    def _make_actions_widget(self, booking_id, status):
        """Build a widget containing action buttons for a booking table row.

        The available actions depend on the booking status. Pending bookings
        include Approve and Reject buttons in addition to View, Edit, and Delete.

        Args:
            booking_id (int): The primary key of the booking.
            status (str): The current booking status ('Pending', 'Approved',
                or 'Rejected').

        Returns:
            QWidget: A container widget with horizontally laid out action buttons.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        layout.addWidget(
            self._make_icon_btn(
                "view.png",
                "View",
                "#F3E5F5",
                "#E1BEE7",
                lambda _, bid=booking_id: self._view_booking(bid),
            )
        )
        if status == "Pending":
            layout.addWidget(
                self._make_icon_btn(
                    "approve.png",
                    "Approve",
                    "#E8F5E9",
                    "#C8E6C9",
                    lambda _, bid=booking_id: self._approve_booking_inline(bid),
                )
            )
            layout.addWidget(
                self._make_icon_btn(
                    "reject.png",
                    "Reject",
                    "#FFF3E0",
                    "#FFE0B2",
                    lambda _, bid=booking_id: self._reject_booking_inline(bid),
                )
            )
        layout.addWidget(
            self._make_icon_btn(
                "edit.png",
                "Edit",
                "#E3F2FD",
                "#BBDEFB",
                lambda _, bid=booking_id: self._edit_booking(bid),
            )
        )
        layout.addWidget(
            self._make_icon_btn(
                "delete.png",
                "Delete",
                "#FFEBEE",
                "#FFCDD2",
                lambda _, bid=booking_id: self._delete_booking(bid),
            )
        )
        layout.addStretch()
        return container

    def _view_booking(self, booking_id):
        """Display a read-only dialog showing the full details of a booking.

        Args:
            booking_id (int): The primary key of the booking to view.
        """
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return

        status_colors = {
            "Pending": "#FF9800",
            "Approved": "#4CAF50",
            "Rejected": "#F44336",
        }
        status_color = status_colors.get(b["status"], "#333")

        dlg = QDialog(self._shell)
        uic.loadUi(os.path.join(UI_DIR, "BookingDetails.ui"), dlg)

        dlg.lblHeader.setText(f"Booking #{b['id']}")
        dlg.lblBadge.setText(b["status"])
        dlg.lblBadge.setStyleSheet(
            f"QLabel {{ background: {status_color}; color: white; font-size: 12px;"
            f" font-weight: bold; padding: 4px 0; }}"
        )

        dlg.editUser.setText(b["username"])
        dlg.editRoom.setText(f"{b['room_name']}  ({b['room_type']})")
        dlg.editDate.setText(b.get("date", ""))
        dlg.editStart.setText(b.get("time_start", ""))
        dlg.editEnd.setText(b.get("time_end", ""))
        dlg.editPurpose.setPlainText(b.get("reason", "") or "")
        dlg.editLockPw.setText(b.get("locker_password") or "---")

        if b.get("reject_reason"):
            dlg.editRejectReason.setText(b["reject_reason"])
        else:
            dlg.labelRejectReason.setVisible(False)
            dlg.editRejectReason.setVisible(False)

        dlg.pushButtonClose.clicked.connect(dlg.accept)
        dlg.exec()

    def _approve_booking_inline(self, booking_id):
        """Approve a booking and display the generated locker password.

        Args:
            booking_id (int): The primary key of the booking to approve.
        """
        password = approve_booking(booking_id)
        QMessageBox.information(
            self._shell,
            "Approved",
            f"Booking approved.\nLocker password: {password}",
        )
        self._load_table()

    def _reject_booking_inline(self, booking_id):
        """Open a rejection dialog and reject a booking with a reason.

        Args:
            booking_id (int): The primary key of the booking to reject.
        """
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return
        dlg = self._build_booking_dialog(booking=b, reject_mode=True)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            reason = dlg.editRejectReason.text().strip()
            if not reason:
                QMessageBox.warning(
                    self._shell, "Error", "Please enter a rejection reason."
                )
                return
            reject_booking(booking_id, reason)
            self._load_table()

    # -- Actions --------------------------------------------------

    def _add_booking(self):
        """Open a dialog to create a new booking and save it to the database."""
        dlg = self._build_booking_dialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            user_id = dlg.comboUser.currentData()
            room_id = dlg.comboRoom.currentData()
            date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
            start_str = dlg.timeEditStart.time().toString("HH:mm")
            end_str = dlg.timeEditEnd.time().toString("HH:mm")
            reason = dlg.editReason.toPlainText().strip()
            if not reason:
                QMessageBox.warning(self._shell, "Error", "Please enter a reason.")
                return
            if create_booking(user_id, room_id, date_str, start_str, end_str, reason):
                self._load_table()
            else:
                QMessageBox.warning(self._shell, "Error", "Failed to create booking.")

    def _edit_booking(self, booking_id):
        """Open a dialog to edit an existing booking.

        Args:
            booking_id (int): The primary key of the booking to edit.
        """
        bookings = get_all_bookings()
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return
        dlg = self._build_booking_dialog(booking=b)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
            start_str = dlg.timeEditStart.time().toString("HH:mm")
            end_str = dlg.timeEditEnd.time().toString("HH:mm")
            reason = dlg.editReason.toPlainText().strip()
            status = dlg.comboStatus.currentText()
            if not reason:
                QMessageBox.warning(self._shell, "Error", "Please enter a reason.")
                return
            admin_update_booking(
                booking_id, date_str, start_str, end_str, reason, status
            )
            self._load_table()

    def _delete_booking(self, booking_id):
        """Delete a booking after user confirmation.

        Args:
            booking_id (int): The primary key of the booking to delete.
        """
        reply = QMessageBox.question(self._shell, "Confirm", "Delete this booking?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_booking(booking_id)
            self._load_table()

    def _import_csv(self):
        """Import bookings from a CSV file into the database.

        Expected CSV columns: username, room_id, date, start_time, end_time,
        reason. Displays a summary of imported and skipped rows with error
        details upon completion.
        """
        import csv
        from models.user_model import get_all_users

        path, _ = QFileDialog.getOpenFileName(
            self._shell, "Open CSV", "", "CSV Files (*.csv)"
        )
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

                    if create_booking(
                        user_pk, room_pk, date_str, start_str, end_str, reason
                    ):
                        imported += 1
                    else:
                        errors.append(
                            f"Row {i}: conflict or error for '{username}' in '{room_id_str}'"
                        )
                        skipped += 1
        except Exception as e:
            QMessageBox.critical(self._shell, "Error", f"Failed to read file:\n{e}")
            return

        self._load_table()
        msg = f"Imported: {imported}  |  Skipped: {skipped}"
        if errors:
            msg += "\n\nDetails:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n... and {len(errors) - 10} more"
        QMessageBox.information(self._shell, "Import Complete", msg)

    def _export_csv(self):
        """Export the currently filtered bookings to a CSV file.

        Applies the active status filter and search keyword before exporting.
        The user is prompted to choose a save location.
        """
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
                or keyword in b.get("date", "").lower()
            ]

        if not bookings:
            QMessageBox.information(self._shell, "Export CSV", "No data to export.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self._shell,
            "Save CSV",
            "bookings.csv",
            "CSV Files (*.csv)",
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
                    writer.writerow(
                        [
                            b["username"],
                            b["room_name"],
                            b["room_type"],
                            b.get("date", ""),
                            b.get("time_start", ""),
                            b.get("time_end", ""),
                            b["reason"],
                            b["status"],
                            b.get("locker_password") or "",
                        ]
                    )
            QMessageBox.information(
                self._shell,
                "Export CSV",
                f"Exported {len(bookings)} bookings successfully.",
            )
        except Exception as e:
            QMessageBox.critical(self._shell, "Error", f"Failed to export:\n{e}")

    def _build_booking_dialog(self, booking=None, reject_mode=False):
        """Build and configure a booking dialog for creating, editing, or rejecting.

        Args:
            booking (dict or None): An existing booking record to pre-fill the
                dialog fields. If None, the dialog is configured for creating
                a new booking. Defaults to None.
            reject_mode (bool): If True, the dialog is configured for rejection
                with most fields disabled and a rejection reason field visible.
                Defaults to False.

        Returns:
            QDialog: The configured booking dialog.
        """
        from models.user_model import get_all_users

        dlg = QDialog(self._shell)
        uic.loadUi(os.path.join(UI_DIR, "AdminBookingDialog.ui"), dlg)

        if reject_mode:
            dlg.setWindowTitle("Reject Booking")
            dlg.lblTitle.setText("Reject Booking")
        elif booking:
            dlg.setWindowTitle("Edit Booking")
            dlg.lblTitle.setText("Edit Booking")

        users = get_all_users()
        for u in users:
            dlg.comboUser.addItem(u["username"], u["id"])

        rooms = get_all_rooms()
        for r in rooms:
            dlg.comboRoom.addItem(f"{r['room_id']} - {r['room_type']}", r["id"])

        dlg.dateEdit.setDate(QDate.currentDate())
        dlg.timeEditStart.setTime(QTime(7, 0))
        dlg.timeEditEnd.setTime(QTime(9, 0))

        if booking:
            for i in range(dlg.comboUser.count()):
                if dlg.comboUser.itemData(i) == booking.get("user_id"):
                    dlg.comboUser.setCurrentIndex(i)
                    break
            for i in range(dlg.comboRoom.count()):
                if dlg.comboRoom.itemText(i).startswith(booking["room_name"]):
                    dlg.comboRoom.setCurrentIndex(i)
                    break

            parsed_date = QDate.fromString(booking.get("date", ""), "yyyy-MM-dd")
            if parsed_date.isValid():
                dlg.dateEdit.setDate(parsed_date)
            parsed_start = QTime.fromString(booking.get("time_start", ""), "HH:mm")
            parsed_end = QTime.fromString(booking.get("time_end", ""), "HH:mm")
            if parsed_start.isValid():
                dlg.timeEditStart.setTime(parsed_start)
            if parsed_end.isValid():
                dlg.timeEditEnd.setTime(parsed_end)

            dlg.editReason.setPlainText(booking["reason"])
            dlg.comboStatus.setCurrentText(booking["status"])

            if reject_mode:
                dlg.comboUser.setEnabled(False)
                dlg.comboRoom.setEnabled(False)
                dlg.dateEdit.setEnabled(False)
                dlg.timeEditStart.setEnabled(False)
                dlg.timeEditEnd.setEnabled(False)
                dlg.editReason.setEnabled(False)
                dlg.labelStatus.setVisible(False)
                dlg.comboStatus.setVisible(False)
                dlg.editRejectReason.setText(booking.get("reject_reason") or "")
            else:
                dlg.labelRejectReason.setVisible(False)
                dlg.editRejectReason.setVisible(False)
        else:
            dlg.labelStatus.setVisible(False)
            dlg.comboStatus.setVisible(False)
            dlg.labelRejectReason.setVisible(False)
            dlg.editRejectReason.setVisible(False)

        dlg.pushButtonCancel.clicked.connect(dlg.reject)
        dlg.pushButtonSave.clicked.connect(dlg.accept)
        return dlg
