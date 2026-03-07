import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication,
    QDialog, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QInputDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6 import uic

from widgets.navbar import NavBar
from widgets.sidebar import SideBar
from models.booking_model import get_all_bookings, approve_booking, reject_booking, get_dashboard_stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(BASE_DIR, "ui")


class BaseWindow(QMainWindow):
    """
    Window mặc định chứa sẵn NavBar + SideBar.
    Các controller kế thừa class này, chỉ cần:
      1. Gọi super().__init__(...)
      2. Load .ui content vào self.content_area
         hoặc tự build content bằng code rồi add vào self.content_layout
    """

    def __init__(self, user, role_text="Admin", show_search=False,
                 show_sidebar=True, title="SmartLocker UEL"):
        super().__init__()
        self.current_user = user
        self.setWindowTitle(title)
        self.setMinimumSize(800, 500)
        self.resize(1000, 600)

        # F11 toggle fullscreen
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        shortcut.activated.connect(self._toggle_fullscreen)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # NavBar
        self.navbar = NavBar(role_text=role_text, show_search=show_search)
        main_layout.addWidget(self.navbar)
        if role_text == "Admin":
            self.navbar.btnRole.clicked.connect(self._show_booking_management)

        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # SideBar (optional)
        self.sidebar = None
        if show_sidebar:
            self.sidebar = SideBar()
            body.addWidget(self.sidebar)
            self._connect_sidebar()

        # Content area — controllers sẽ add widget vào đây
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        body.addWidget(self.content_area, 1)  # stretch factor = 1

        main_layout.addLayout(body)

    def _connect_sidebar(self):
        """Kết nối sidebar navigation mặc định. Override nếu cần."""
        self.sidebar.btnOverview.clicked.connect(self._go_overview)
        self.sidebar.btnBookings.clicked.connect(self._go_bookings)
        self.sidebar.btnEdit.clicked.connect(self._go_edit)
        self.sidebar.btnUsers.clicked.connect(self._go_users)
        self.sidebar.btnLogout.clicked.connect(self._logout)
        self.sidebar.btnQuit.clicked.connect(self._quit)

    def load_content_ui(self, ui_filename):
        """Load file .ui vào content_area."""
        content_widget = QWidget()
        uic.loadUi(os.path.join(UI_DIR, ui_filename), content_widget)
        self.content_layout.addWidget(content_widget)
        return content_widget

    # ── Navigation mặc định ──────────────────────────────

    def _go_overview(self):
        from controllers.overview_admin import OverviewAdminController
        self._win = OverviewAdminController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_bookings(self):
        from controllers.booking_overview import BookingOverviewController
        self._win = BookingOverviewController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_edit(self, preselect_room=None):
        from controllers.edit_room import EditRoomController
        self._win = EditRoomController(self.current_user, preselect_room=preselect_room)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _go_users(self):
        from controllers.users_management import UsersManagementController
        self._win = UsersManagementController(self.current_user)
        self._transfer_window_state(self._win)
        self._win.show()
        self.close()

    def _transfer_window_state(self, target):
        if self.isFullScreen():
            target.showFullScreen()
        elif self.isMaximized():
            target.showMaximized()
        else:
            target.resize(self.size())
            target.move(self.pos())

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _logout(self):
        reply = QMessageBox.question(self, "Log out", "Are you sure you want to log out?")
        if reply != QMessageBox.StandardButton.Yes:
            return
        from controllers.main_window import MainWindowController
        self._login = MainWindowController()
        self._login.show()
        self.close()

    @staticmethod
    def _quit():
        reply = QMessageBox.question(
            None, "Quit", "Are you sure you want to quit?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()

    # ── Booking Management (Admin) ────────────────────────

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
        if hasattr(self, "_load_rooms"):
            self._load_rooms()

    def _reject(self, booking_id, dlg):
        reason, ok = QInputDialog.getText(
            self, "Reject", "Enter rejection reason:"
        )
        if ok and reason.strip():
            reject_booking(booking_id, reason.strip())
            QMessageBox.information(self, "Rejected", "Booking has been rejected.")
            self._populate_approvals(dlg, dlg.comboFilter.currentText())
            if hasattr(self, "_load_rooms"):
                self._load_rooms()
