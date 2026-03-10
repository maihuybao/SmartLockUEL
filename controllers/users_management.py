from PyQt6.QtWidgets import (
    QTableWidgetItem, QMessageBox, QApplication, QHeaderView,
)

from widgets.base_window import BaseWindow
from models.user_model import get_all_users, create_user, update_user, delete_user


class UsersManagementController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Users Management",
        )
        self._selected_pk = None

        # Load content from .ui
        self.ui = self.load_content_ui("Users.ui")

        self._connect_signals()
        self._load_table()

    def _connect_sidebar(self):
        """Override: Users is current page."""
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(self._go_edit)
        self.sidebar.pushButtonUsers.clicked.connect(lambda: None)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        self.ui.pushButtonCreate.clicked.connect(self._create)
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonDelete.clicked.connect(self._delete)
        self.ui.pushButtonReload.clicked.connect(self._load_table)
        self.ui.lineEditSearch.returnPressed.connect(self._search)
        self.ui.lineEditSearch.textChanged.connect(self._search)
        self.ui.tableWidget.cellClicked.connect(self._on_row_click)

    # ── Table ────────────────────────────────────────────

    def _load_table(self):
        users = get_all_users()
        self._populate_table(users)
        self._clear_form()

    def _search(self):
        keyword = self.ui.lineEditSearch.text().strip().lower()
        users = get_all_users()
        if keyword:
            users = [u for u in users if keyword in u["username"].lower() or keyword in u["role"].lower()]
        self._populate_table(users)

    def _populate_table(self, users):
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for u in users:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(u["username"]))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem("••••••"))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(u["role"]))

    def _on_row_click(self, row, _col):
        username = self.ui.tableWidget.item(row, 0).text()
        role = self.ui.tableWidget.item(row, 2).text()
        self.ui.LineEditUsername.setText(username)
        self.ui.LineEditPassword.clear()
        self.ui.LineEditRole.setText(role)
        users = get_all_users()
        match = [u for u in users if u["username"] == username]
        self._selected_pk = match[0]["id"] if match else None

    def _clear_form(self):
        self.ui.LineEditUsername.clear()
        self.ui.LineEditPassword.clear()
        self.ui.LineEditRole.clear()
        self._selected_pk = None

    # ── CRUD ─────────────────────────────────────────────

    def _create(self):
        username = self.ui.LineEditUsername.text().strip()
        password = self.ui.LineEditPassword.text().strip()
        role = self.ui.LineEditRole.text().strip().lower()
        if not username or not password or role not in ("admin", "user"):
            QMessageBox.warning(self, "Error", "Please enter Username, Password and Role (admin/user).")
            return
        if create_user(username, password, role):
            QMessageBox.information(self, "Success", "User created successfully.")
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Username already exists.")

    def _update(self):
        if not self._selected_pk:
            QMessageBox.warning(self, "Error", "Please select a user to update.")
            return
        username = self.ui.LineEditUsername.text().strip()
        password = self.ui.LineEditPassword.text().strip()
        role = self.ui.LineEditRole.text().strip().lower()
        if not username or role not in ("admin", "user"):
            QMessageBox.warning(self, "Error", "Please enter full information.")
            return
        if update_user(self._selected_pk, username, password, role):
            QMessageBox.information(self, "Success", "Updated user successfully.")
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to update user.")

    def _delete(self):
        if not self._selected_pk:
            QMessageBox.warning(self, "Error", "Please select a user to delete.")
            return
        if self._selected_pk == self.current_user["id"]:
            QMessageBox.warning(self, "Error", "You cannot delete your own account.")
            return
        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to delete this user?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_user(self._selected_pk)
            QMessageBox.information(self, "Thành công", "Đã xóa user.")
            self._load_table()
