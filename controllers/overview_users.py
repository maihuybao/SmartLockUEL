from PyQt6.QtWidgets import (
    QDialog,
    QMessageBox,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QWidget,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QDate, QTime, QSize
from PyQt6.QtGui import QColor, QIcon
from PyQt6 import uic
import os

from paths import resource_dir
from i18n import tr

_BASE = resource_dir()
IMAGES_DIR = os.path.join(_BASE, "images")


def _png_icon(name):
    """Load a PNG icon from the images directory.

    Args:
        name (str): The filename of the icon (e.g., 'view.png').

    Returns:
        QIcon: The loaded icon, or an empty QIcon if the file does not exist.
    """
    path = os.path.join(IMAGES_DIR, name)
    if not os.path.exists(path):
        return QIcon()
    return QIcon(path)


from widgets.base_window import BaseWindow
from widgets.room_card import create_room_card, get_display_status
from models.room_model import get_all_rooms, get_rooms_by_status, search_rooms
from models.booking_model import (
    create_booking,
    get_bookings_by_user,
    get_bookings_by_room_date,
    has_conflict,
    cancel_booking,
)

BASE_DIR = _BASE
UI_DIR = os.path.join(BASE_DIR, "ui")

OP_START = QTime(6, 0)
OP_END = QTime(22, 0)


class OverviewUsersController(BaseWindow):
    """User dashboard controller for browsing rooms and managing bookings.

    Provides a filterable room grid with three independent filter dimensions
    (status, capacity, time range), booking creation with conflict detection,
    and booking history management.

    Args:
        user (dict): The authenticated user record.
    """

    def __init__(self, user):
        """Initialize the user dashboard with room grid, filters, and booking controls."""
        super().__init__(
            user,
            role_text="User",
            show_search=True,
            show_sidebar=False,
            title="SmartLocker UEL - User",
        )
        self._current_filter = "All"
        self._capacity_filter = "All"

        self.ui = self.load_content_ui("OverviewUsers.ui")

        self._connect_signals()
        self.ui.pushButtonAll.setChecked(True)
        self._load_rooms()

    def _connect_signals(self):
        """Connect filter buttons, search field, and action buttons to handlers."""
        self.ui.pushButtonAll.clicked.connect(lambda: self._apply_filter("All"))
        self.ui.pushButtonAvailable.clicked.connect(
            lambda: self._apply_filter("Available")
        )
        self.ui.pushButtonOccupied.clicked.connect(
            lambda: self._apply_filter("Occupied")
        )
        self.ui.pushButtonBooked.clicked.connect(lambda: self._apply_filter("Full"))

        self.ui.pushButtonCapAll.clicked.connect(lambda: self._apply_capacity("All"))
        self.ui.pushButtonCap50.clicked.connect(lambda: self._apply_capacity("50"))
        self.ui.pushButtonCap100.clicked.connect(lambda: self._apply_capacity("100"))

        self.navbar.lineEditSearch.textChanged.connect(self._on_search)

        self.ui.pushButtonHistory.clicked.connect(self._show_history)
        self.ui.pushButtonBooking.clicked.connect(self._open_booking_dialog)
        self.ui.pushButtonLogout.clicked.connect(self._logout)
        self.ui.pushButtonQuit.clicked.connect(self._quit)

    # -- Room grid ------------------------------------------------

    def _apply_filter(self, status):
        """Apply a room status filter and reload the room grid.

        Args:
            status (str): The status filter ('All', 'Available', 'Occupied', 'Full').
        """
        self._current_filter = status
        self._load_rooms()

    def _apply_capacity(self, cap):
        """Apply a capacity filter and reload the room grid.

        Args:
            cap (str): The capacity filter ('All', '50' for <=50, '100' for >=100).
        """
        self._capacity_filter = cap
        self._load_rooms()

    def _load_rooms(self):
        """Load rooms applying all active filters (status, capacity, time, search)."""
        from datetime import date as _date

        keyword = (
            self.navbar.lineEditSearch.text().strip()
            if self.navbar.lineEditSearch
            else ""
        )

        if keyword:
            rooms = search_rooms(keyword)
        elif self._current_filter == "Full":
            rooms = [r for r in get_all_rooms() if get_display_status(r) == "Full"]
        elif self._current_filter == "All":
            rooms = get_all_rooms()
        else:
            rooms = get_rooms_by_status(self._current_filter)

        # Loai bo phong Full khi filter Available
        if self._current_filter == "Available":
            rooms = [r for r in rooms if get_display_status(r) != "Full"]

        # Capacity filter
        if self._capacity_filter == "50":
            rooms = [r for r in rooms if r["capacity"] <= 50]
        elif self._capacity_filter == "100":
            rooms = [r for r in rooms if r["capacity"] >= 100]

        self._render_room_cards(rooms)

    def _render_room_cards(self, rooms):
        """Store room data and trigger a grid reflow.

        Args:
            rooms (list[dict]): The list of room dictionaries to render.
        """
        self._rooms_data = rooms
        self._reflow_grid()

    def _reflow_grid(self):
        """Recalculate the grid layout and re-render all room cards."""
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
        """Handle the widget show event by reflowing the room card grid."""
        super().showEvent(event)
        self._reflow_grid()

    def resizeEvent(self, event):
        """Handle the widget resize event by reflowing the room card grid."""
        super().resizeEvent(event)
        self._reflow_grid()

    def _create_room_card(self, room):
        """Create a room card widget with a booking context menu.

        Args:
            room (dict): The room dictionary to create a card for.

        Returns:
            QWidget: The room card widget.
        """
        return create_room_card(room, on_context=self._on_card_context)

    def _on_card_context(self, room, global_pos):
        """Display a context menu with a 'Book Room' action for a room card.

        Args:
            room (dict): The room dictionary for the right-clicked card.
            global_pos (QPoint): The global screen position for the context menu.
        """
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction

        menu = QMenu(self)
        act = QAction(tr("btn_book_room"), self)
        act.triggered.connect(lambda: self._open_booking_dialog(room))
        menu.addAction(act)
        menu.exec(global_pos)

    def _apply_filter(self, status):
        """Apply a room status filter and reload the room grid.

        Args:
            status (str): The status filter ('All', 'Available', 'Occupied', 'Full').
        """
        self._current_filter = status
        self._load_rooms()

    def _on_search(self):
        """Handle search input changes by reloading the room grid."""
        self._load_rooms()

    # -- Booking dialog -------------------------------------------

    def _open_booking_dialog(self, preselect_room=None):
        """Open a booking dialog for creating a new room booking.

        Validates time range, checks for conflicts, and creates the booking
        upon successful submission.

        Args:
            preselect_room (dict or None): An optional room dictionary to
                pre-select in the room combo box. Defaults to None.
        """
        available = [r for r in get_all_rooms() if r["status"] in ("Available",)]
        if not available:
            QMessageBox.information(self, tr("common_confirm"), tr("msg_no_available_rooms"))
            return

        dlg = QDialog(self)
        uic.loadUi(os.path.join(UI_DIR, "BookingDialog.ui"), dlg)

        for r in available:
            dlg.comboRoom.addItem(
                f"{r['room_id']} - {r['room_type']} ({r['capacity']} Seats)",
                r["id"],
            )

        if preselect_room:
            for i in range(dlg.comboRoom.count()):
                if dlg.comboRoom.itemData(i) == preselect_room["id"]:
                    dlg.comboRoom.setCurrentIndex(i)
                    break

        dlg.dateEdit.setDate(QDate.currentDate())
        dlg.dateEdit.setMinimumDate(QDate.currentDate())

        dlg.timeEditStart.setMinimumTime(QTime(6, 0))
        dlg.timeEditStart.setMaximumTime(QTime(21, 59))
        dlg.timeEditStart.setTime(QTime(7, 0))

        dlg.timeEditEnd.setMinimumTime(QTime(6, 1))
        dlg.timeEditEnd.setMaximumTime(QTime(22, 0))
        dlg.timeEditEnd.setTime(QTime(9, 0))

        self._refresh_availability(dlg)
        dlg.comboRoom.currentIndexChanged.connect(
            lambda _: self._refresh_availability(dlg)
        )
        dlg.dateEdit.dateChanged.connect(lambda _: self._refresh_availability(dlg))

        dlg.pushButtonCancel.clicked.connect(dlg.reject)
        dlg.pushButtonSubmit.clicked.connect(dlg.accept)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            room_pk = dlg.comboRoom.currentData()
            date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
            start_t = dlg.timeEditStart.time()
            end_t = dlg.timeEditEnd.time()
            start_str = start_t.toString("HH:mm")
            end_str = end_t.toString("HH:mm")
            purpose = dlg.lineEditPurpose.toPlainText().strip()

            if not purpose:
                QMessageBox.warning(self, tr("common_error"), tr("msg_enter_purpose"))
                return
            if start_t < OP_START or end_t > OP_END:
                QMessageBox.warning(
                    self,
                    tr("common_error"),
                    tr("msg_booking_hours"),
                )
                return
            if end_t <= start_t:
                QMessageBox.warning(self, tr("common_error"), tr("msg_end_after_start"))
                return
            if has_conflict(room_pk, date_str, start_str, end_str):
                QMessageBox.warning(
                    self,
                    tr("msg_conflict_title"),
                    tr("msg_time_conflict"),
                )
                return

            if create_booking(self.current_user["id"], room_pk, date_str, start_str, end_str, purpose):
                QMessageBox.information(
                    self, tr("common_success"), tr("msg_booking_success")
                )
                self._load_rooms()
            else:
                QMessageBox.warning(self, tr("common_error"), tr("msg_booking_failed"))

    def _refresh_availability(self, dlg):
        """Update the time availability table in the booking dialog.

        Renders a color-coded hourly grid showing which slots are available,
        pending, or approved for the selected room and date.

        Args:
            dlg (QDialog): The booking dialog containing the availability table.
        """
        room_pk = dlg.comboRoom.currentData()
        date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
        if not room_pk:
            return

        bookings = get_bookings_by_room_date(room_pk, date_str)

        # Parse into (start_min, end_min, status)
        intervals = []
        for b in bookings:
            def _m(t):
                hh, mm = map(int, t.strip().split(":"))
                return hh * 60 + mm

            intervals.append((_m(b["time_start"]), _m(b["time_end"]), b["status"]))

        # Build 16-column table (06:00 – 21:00, 1 hour each)
        table = dlg.tableAvailability
        hours = list(range(6, 22))
        table.setColumnCount(len(hours))
        table.setRowCount(1)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setHorizontalHeaderLabels([f"{h:02d}" for h in hours])
        table.verticalHeader().setDefaultSectionSize(28)
        table.setShowGrid(True)

        COLOR_APPROVED = QColor("#EF9A9A")  # red-ish
        COLOR_PENDING = QColor("#FFE082")  # amber
        COLOR_FREE = QColor("#A5D6A7")  # green

        for col, hour in enumerate(hours):
            slot_s = hour * 60
            slot_e = (hour + 1) * 60
            cell_status = None
            for bs, be, bst in intervals:
                if bs < slot_e and be > slot_s:
                    if bst == "Approved":
                        cell_status = "Approved"
                        break
                    cell_status = "Pending"

            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if cell_status == "Approved":
                item.setBackground(COLOR_APPROVED)
                item.setToolTip(tr("availability_approved"))
            elif cell_status == "Pending":
                item.setBackground(COLOR_PENDING)
                item.setToolTip(tr("availability_pending"))
            else:
                item.setBackground(COLOR_FREE)
                item.setToolTip(tr("availability_free"))
            table.setItem(0, col, item)

    # -- Booking history ------------------------------------------

    def _show_history(self):
        """Display the booking history dialog for the current user."""
        dlg = QDialog(self)
        uic.loadUi(os.path.join(UI_DIR, "BookingHistory.ui"), dlg)
        dlg.tableWidgetHistory.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        dlg.pushButtonClose.clicked.connect(dlg.accept)
        dlg.comboFilter.currentTextChanged.connect(
            lambda f: self._populate_history(dlg, f)
        )
        self._populate_history(dlg, "All Status")
        dlg.exec()

    def _populate_history(self, dlg, filter_text):
        """Populate the booking history table with filtered booking data.

        Args:
            dlg (QDialog): The history dialog containing the bookings table.
            filter_text (str): The status filter text ('All Status', 'Pending',
                'Approved', or 'Rejected').
        """
        bookings = get_bookings_by_user(self.current_user["id"])
        if filter_text != "All Status":
            bookings = [b for b in bookings if b["status"] == filter_text]

        table = dlg.tableWidgetHistory
        table.verticalHeader().setDefaultSectionSize(36)
        table.verticalHeader().setMinimumSectionSize(36)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(9, 100)
        table.setRowCount(len(bookings))
        for row, b in enumerate(bookings):
            table.setItem(row, 0, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 2, QTableWidgetItem(b.get("date", "")))
            table.setItem(row, 3, QTableWidgetItem(b.get("time_start", "")))
            table.setItem(row, 4, QTableWidgetItem(b.get("time_end", "")))
            table.setItem(row, 5, QTableWidgetItem(b["reason"]))

            status_item = QTableWidgetItem(b["status"])
            status_colors = {
                "Pending": "#FF9800",
                "Approved": "#4CAF50",
                "Rejected": "#F44336",
            }
            status_item.setForeground(QColor(status_colors.get(b["status"], "#333")))
            table.setItem(row, 6, status_item)

            table.setItem(row, 7, QTableWidgetItem(b.get("locker_password") or ""))

            reject_reason = b.get("reject_reason") or ""
            reject_item = QTableWidgetItem(reject_reason)
            if reject_reason:
                reject_item.setForeground(QColor("#F44336"))
            table.setItem(row, 8, reject_item)

            table.setCellWidget(row, 9, None)
            container = QWidget()
            btn_layout = QHBoxLayout(container)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)

            btn_view = QPushButton()
            btn_view.setToolTip(tr("tooltip_view"))
            btn_view.setFixedSize(22, 22)
            btn_view.setIcon(_png_icon("view.png"))
            btn_view.setIconSize(QSize(14, 14))
            btn_view.setStyleSheet(
                "QPushButton{background:#F3E5F5;border:none;border-radius:6px;}"
                "QPushButton:hover{background:#E1BEE7;}"
            )
            btn_view.clicked.connect(
                lambda _, bid=b["id"]: self._view_booking(bid, dlg)
            )
            btn_layout.addWidget(btn_view)

            if b["status"] == "Pending":
                btn_edit = QPushButton()
                btn_edit.setToolTip(tr("tooltip_edit"))
                btn_edit.setFixedSize(22, 22)
                btn_edit.setIcon(_png_icon("edit.png"))
                btn_edit.setIconSize(QSize(14, 14))
                btn_edit.setStyleSheet(
                    "QPushButton{background:#E3F2FD;border:none;border-radius:6px;}"
                    "QPushButton:hover{background:#BBDEFB;}"
                )
                btn_edit.clicked.connect(
                    lambda _, bid=b["id"]: self._edit_booking(bid, dlg)
                )

                btn_cancel = QPushButton()
                btn_cancel.setToolTip(tr("tooltip_cancel"))
                btn_cancel.setFixedSize(22, 22)
                btn_cancel.setIcon(_png_icon("delete.png"))
                btn_cancel.setIconSize(QSize(14, 14))
                btn_cancel.setStyleSheet(
                    "QPushButton{background:#FFEBEE;border:none;border-radius:6px;}"
                    "QPushButton:hover{background:#FFCDD2;}"
                )
                btn_cancel.clicked.connect(
                    lambda _, bid=b["id"]: self._cancel_booking(bid, dlg)
                )

                btn_layout.addWidget(btn_edit)
                btn_layout.addWidget(btn_cancel)

            btn_layout.addStretch()
            table.setCellWidget(row, 9, container)

        dlg.lblCount.setText(tr("n_bookings", n=len(bookings)))

    def _view_booking(self, booking_id, parent_dlg):
        """Display a read-only dialog showing booking details for the user.

        Args:
            booking_id (int): The primary key of the booking to view.
            parent_dlg (QDialog): The parent dialog (history dialog).
        """
        from models.booking_model import get_bookings_by_user

        bookings = get_bookings_by_user(self.current_user["id"])
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return

        status_colors = {"Pending": "#FF9800", "Approved": "#4CAF50", "Rejected": "#F44336"}
        status_color = status_colors.get(b["status"], "#333")

        dlg = QDialog(parent_dlg)
        uic.loadUi(os.path.join(UI_DIR, "BookingDetails.ui"), dlg)

        dlg.lblHeader.setText(f"Booking #{b['id']}")
        dlg.lblBadge.setText(b["status"])
        dlg.lblBadge.setStyleSheet(
            f"QLabel {{ background: {status_color}; color: white; font-size: 12px;"
            f" font-weight: bold; padding: 4px 0; }}"
        )

        dlg.labelUser.setVisible(False)
        dlg.editUser.setVisible(False)
        dlg.editRoom.setText(f"{b['room_name']}  ({b['room_type']})")
        dlg.editDate.setText(b.get("date", ""))
        dlg.editStart.setText(b.get("time_start", ""))
        dlg.editEnd.setText(b.get("time_end", ""))
        dlg.editPurpose.setPlainText(b.get("reason", "") or "")
        dlg.editLockPw.setText(b.get("locker_password") or "—")

        if b.get("reject_reason"):
            dlg.editRejectReason.setText(b["reject_reason"])
        else:
            dlg.labelRejectReason.setVisible(False)
            dlg.editRejectReason.setVisible(False)

        dlg.pushButtonClose.clicked.connect(dlg.accept)
        dlg.exec()

    def _edit_booking(self, booking_id, history_dlg):
        """Open a dialog to edit a pending booking and refresh the history.

        Args:
            booking_id (int): The primary key of the booking to edit.
            history_dlg (QDialog): The parent history dialog to refresh
                after a successful edit.
        """
        from models.booking_model import update_booking

        bookings = get_bookings_by_user(self.current_user["id"])
        b = next((x for x in bookings if x["id"] == booking_id), None)
        if not b:
            return

        dlg = QDialog(self)
        uic.loadUi(os.path.join(UI_DIR, "BookingDialog.ui"), dlg)
        dlg.setWindowTitle(tr("dlg_edit_booking"))
        dlg.lblTitle.setText(tr("dlg_edit_booking"))
        dlg.pushButtonSubmit.setText(tr("dlg_save_changes"))

        # Room combo — pre-select, disable change
        rooms = get_all_rooms()
        for r in rooms:
            dlg.comboRoom.addItem(
                f"{r['room_id']} - {r['room_type']} ({r['capacity']} Seats)", r["id"]
            )
        for i in range(dlg.comboRoom.count()):
            if dlg.comboRoom.itemData(i) == b["room_id"]:
                dlg.comboRoom.setCurrentIndex(i)
                break
        dlg.comboRoom.setEnabled(False)

        # Pre-fill date/time
        parsed_date = QDate.fromString(b.get("date", ""), "yyyy-MM-dd")
        if parsed_date.isValid():
            dlg.dateEdit.setDate(parsed_date)
        ps = QTime.fromString(b.get("time_start", ""), "HH:mm")
        pe = QTime.fromString(b.get("time_end", ""), "HH:mm")
        if ps.isValid():
            dlg.timeEditStart.setTime(ps)
        if pe.isValid():
            dlg.timeEditEnd.setTime(pe)

        dlg.lineEditPurpose.setPlainText(b["reason"])
        dlg.dateEdit.setMinimumDate(QDate.currentDate())
        dlg.timeEditStart.setMinimumTime(QTime(6, 0))
        dlg.timeEditStart.setMaximumTime(QTime(21, 59))
        dlg.timeEditEnd.setMinimumTime(QTime(6, 1))
        dlg.timeEditEnd.setMaximumTime(QTime(22, 0))

        self._refresh_availability(dlg)
        dlg.dateEdit.dateChanged.connect(lambda _: self._refresh_availability(dlg))

        dlg.pushButtonCancel.clicked.connect(dlg.reject)
        dlg.pushButtonSubmit.clicked.connect(dlg.accept)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        room_pk = dlg.comboRoom.currentData()
        date_str = dlg.dateEdit.date().toString("yyyy-MM-dd")
        start_t = dlg.timeEditStart.time()
        end_t = dlg.timeEditEnd.time()
        start_str = start_t.toString("HH:mm")
        end_str = end_t.toString("HH:mm")
        purpose = dlg.lineEditPurpose.toPlainText().strip()

        if not purpose:
            QMessageBox.warning(self, tr("common_error"), tr("msg_enter_purpose"))
            return
        if end_t <= start_t:
            QMessageBox.warning(self, tr("common_error"), tr("msg_end_after_start"))
            return
        if has_conflict(room_pk, date_str, start_str, end_str, exclude_id=booking_id):
            QMessageBox.warning(
                self,
                tr("msg_conflict_title"),
                tr("msg_time_conflict"),
            )
            return

        update_booking(booking_id, date_str, start_str, end_str, purpose)
        QMessageBox.information(self, tr("common_success"), tr("msg_booking_updated"))
        self._populate_history(history_dlg, history_dlg.comboFilter.currentText())
        self._load_rooms()

    def _cancel_booking(self, booking_id, dlg):
        """Cancel a pending booking after user confirmation.

        Args:
            booking_id (int): The primary key of the booking to cancel.
            dlg (QDialog): The parent history dialog to refresh after
                cancellation.
        """
        reply = QMessageBox.question(
            self, tr("common_confirm"), tr("msg_cancel_confirm")
        )
        if reply == QMessageBox.StandardButton.Yes:
            cancel_booking(booking_id)
            self._populate_history(dlg, dlg.comboFilter.currentText())
            self._load_rooms()

    def retranslate_ui(self):
        self.ui.pushButtonAll.setText(tr("status_all"))
        self.ui.pushButtonAvailable.setText(tr("status_available"))
        self.ui.pushButtonOccupied.setText(tr("status_occupied"))
        self.ui.pushButtonBooked.setText(tr("status_full"))
        self.ui.pushButtonCapAll.setText(tr("status_all"))
        self.ui.pushButtonCap50.setText(tr("filter_cap_50"))
        self.ui.pushButtonCap100.setText(tr("filter_cap_100"))
        self.ui.lblCapacity.setText(tr("filter_capacity"))
        self.ui.pushButtonHistory.setText(tr("btn_my_bookings"))
        self.ui.pushButtonBooking.setText(tr("btn_booking"))
        self.ui.pushButtonLogout.setText(tr("btn_logout"))
        self.ui.pushButtonQuit.setText(tr("btn_quit"))
        self._load_rooms()
