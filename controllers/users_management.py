from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QFileDialog,
    QPushButton,
    QHBoxLayout,
    QDialog,
)
from PyQt6.QtCore import QSize
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


from models.user_model import get_all_users, create_user, update_user, delete_user


class UsersManagementPage(QWidget):
    """Admin page for managing user accounts with CRUD, filtering, and CSV support.

    Provides a table view of users with inline actions for viewing bookings,
    editing, and deleting. Supports role-based filtering, search, and CSV
    import/export.

    Args:
        shell (AdminShellController): The parent admin shell controller.
    """

    def __init__(self, shell):
        """Initialize the user management page, load UI, and display users."""
        super().__init__()
        self._shell = shell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.ui = QWidget()
        uic.loadUi(os.path.join(UI_DIR, "Users.ui"), self.ui)
        layout.addWidget(self.ui)

        self._connect_signals()
        self._load_table()

    def _connect_signals(self):
        """Connect filter buttons, search field, and action buttons to handlers."""
        self.ui.pushButtonAll.clicked.connect(self._apply_filter)
        self.ui.pushButtonAdmin.clicked.connect(self._apply_filter)
        self.ui.pushButtonUser.clicked.connect(self._apply_filter)
        self.ui.lineEditSearch.textChanged.connect(self._apply_filter)
        self.ui.pushButtonAdd.clicked.connect(self._add_user)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    def refresh(self):
        """Reload the users table data from the database."""
        self._load_table()

    def _load_table(self):
        """Load the users table by applying current filters."""
        self._apply_filter()

    def _apply_filter(self):
        """Filter and display users based on role filter and search keyword."""
        users = get_all_users()
        if self.ui.pushButtonAdmin.isChecked():
            users = [u for u in users if u["role"] == "admin"]
        elif self.ui.pushButtonUser.isChecked():
            users = [u for u in users if u["role"] == "user"]
        keyword = self.ui.lineEditSearch.text().strip().lower()
        if keyword:
            users = [u for u in users if keyword in u["username"].lower()]
        self._populate_table(users)

    def _populate_table(self, users):
        """Populate the users table widget with user data and action buttons.

        Args:
            users (list[dict]): The list of user dictionaries to display.
        """
        table = self.ui.tableWidget
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(2, 100)
        table.verticalHeader().setDefaultSectionSize(32)
        self.ui.lblCount.setText(f"{len(users)} users")
        role_colors = {"admin": "#E91E63", "user": "#4CAF50"}
        for row, u in enumerate(users):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(u["username"]))
            role_item = QTableWidgetItem(u["role"])
            role_item.setForeground(QColor(role_colors.get(u["role"], "#333")))
            table.setItem(row, 1, role_item)
            table.setCellWidget(row, 2, self._make_actions_widget(u))

    def _make_actions_widget(self, user):
        """Build a widget with View Bookings, Edit, and Delete buttons for a user row.

        Args:
            user (dict): The user dictionary for the table row.

        Returns:
            QWidget: A container widget with horizontally laid out action buttons.
        """
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(4)

        btn_view = QPushButton()
        btn_view.setToolTip("View Bookings")
        btn_view.setFixedSize(22, 22)
        btn_view.setIcon(_png_icon("view.png"))
        btn_view.setIconSize(QSize(14, 14))
        btn_view.setStyleSheet(
            "QPushButton{background:#F3E5F5;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#E1BEE7;}"
        )
        btn_view.clicked.connect(lambda _, u=user: self._view_user_bookings(u))

        btn_edit = QPushButton()
        btn_edit.setToolTip("Edit")
        btn_edit.setFixedSize(22, 22)
        btn_edit.setIcon(_png_icon("edit.png"))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setStyleSheet(
            "QPushButton{background:#E3F2FD;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#BBDEFB;}"
        )
        btn_edit.clicked.connect(lambda _, u=user: self._edit_user(u))

        btn_del = QPushButton()
        btn_del.setToolTip("Delete")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(_png_icon("delete.png"))
        btn_del.setIconSize(QSize(14, 14))
        btn_del.setStyleSheet(
            "QPushButton{background:#FFEBEE;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#FFCDD2;}"
        )
        btn_del.clicked.connect(lambda _, u=user: self._delete_user(u["id"]))

        lay.addWidget(btn_view)
        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)
        lay.addStretch()
        return container

    def _build_user_dialog(self, user=None):
        """Build and configure a dialog for creating or editing a user.

        Args:
            user (dict or None): An existing user record to pre-fill the
                dialog fields. If None, the dialog is configured for creating
                a new user. Defaults to None.

        Returns:
            QDialog: The configured user dialog.
        """
        dlg = QDialog(self._shell)
        uic.loadUi(os.path.join(UI_DIR, "UserDialog.ui"), dlg)
        if user:
            dlg.setWindowTitle("Edit User")
            dlg.lblTitle.setText("Edit User")
            dlg.editUsername.setText(user["username"])
            dlg.comboRole.setCurrentText(user["role"])
        dlg.pushButtonCancel.clicked.connect(dlg.reject)
        dlg.pushButtonSave.clicked.connect(dlg.accept)
        return dlg

    def _add_user(self):
        """Open a dialog to create a new user and save it to the database."""
        dlg = self._build_user_dialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        username = dlg.editUsername.text().strip()
        password = dlg.editPassword.text().strip()
        role = dlg.comboRole.currentText()
        if not username or not password:
            QMessageBox.warning(
                self._shell, "Error", "Please enter username and password."
            )
            return
        if create_user(username, password, role):
            self._load_table()
        else:
            QMessageBox.warning(self._shell, "Error", "Username already exists.")

    def _edit_user(self, user):
        """Open a dialog to edit an existing user.

        Args:
            user (dict): The user dictionary to edit.
        """
        dlg = self._build_user_dialog(user)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        username = dlg.editUsername.text().strip()
        password = dlg.editPassword.text().strip()
        role = dlg.comboRole.currentText()
        if not username:
            QMessageBox.warning(self._shell, "Error", "Please enter a username.")
            return
        if update_user(user["id"], username, password, role):
            self._load_table()
        else:
            QMessageBox.warning(self._shell, "Error", "Failed to update user.")

    def _delete_user(self, user_id):
        """Delete a user after confirmation, preventing self-deletion.

        Args:
            user_id (int): The primary key of the user to delete.
        """
        if user_id == self._shell.current_user["id"]:
            QMessageBox.warning(
                self._shell, "Error", "You cannot delete your own account."
            )
            return
        reply = QMessageBox.question(self._shell, "Confirm", "Delete this user?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_user(user_id)
            self._load_table()

    def _view_user_bookings(self, user):
        """Display a dialog showing the booking history for a specific user.

        Args:
            user (dict): The user dictionary containing 'id' and 'username'.
        """
        from models.booking_model import get_bookings_by_user

        bookings = get_bookings_by_user(user["id"])
        dlg = QDialog(self._shell)
        uic.loadUi(os.path.join(UI_DIR, "UserBookingsView.ui"), dlg)
        dlg.setWindowTitle(f"Bookings -- {user['username']}")
        dlg.lblHeader.setText(f"Booking history: {user['username']}")
        table = dlg.tableBookings
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(30)
        status_colors = {
            "Pending": "#FF9800",
            "Approved": "#4CAF50",
            "Rejected": "#F44336",
        }
        table.setRowCount(len(bookings))
        for row, b in enumerate(bookings):
            table.setItem(row, 0, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 2, QTableWidgetItem(b.get("date", "")))
            table.setItem(row, 3, QTableWidgetItem(b.get("time_start", "")))
            table.setItem(row, 4, QTableWidgetItem(b.get("time_end", "")))
            table.setItem(row, 5, QTableWidgetItem(b.get("reason", "")))
            status_item = QTableWidgetItem(b["status"])
            status_item.setForeground(QColor(status_colors.get(b["status"], "#333")))
            table.setItem(row, 6, status_item)
        dlg.lblCount.setText(f"{len(bookings)} bookings")
        dlg.pushButtonClose.clicked.connect(dlg.accept)
        dlg.exec()

    def _import_csv(self):
        """Import users from a CSV file into the database.

        Expected CSV columns: username, password, role. Displays a summary
        of imported and skipped rows upon completion.
        """
        import csv

        path, _ = QFileDialog.getOpenFileName(
            self._shell, "Open CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return
        imported, skipped, errors = 0, 0, []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                for i, row in enumerate(csv.DictReader(f), start=2):
                    username = (row.get("username") or "").strip()
                    password = (row.get("password") or "").strip()
                    role = (row.get("role") or "").strip().lower()
                    if not username or not password or role not in ("admin", "user"):
                        errors.append(f"Row {i}: missing or invalid fields")
                        skipped += 1
                        continue
                    if create_user(username, password, role):
                        imported += 1
                    else:
                        errors.append(f"Row {i}: username '{username}' already exists")
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
        """Export all users to a CSV file chosen by the user."""
        import csv

        path, _ = QFileDialog.getSaveFileName(
            self._shell, "Save CSV", "users.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        users = get_all_users()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["username", "role"])
                writer.writeheader()
                for u in users:
                    writer.writerow({"username": u["username"], "role": u["role"]})
            QMessageBox.information(
                self._shell,
                "Export Complete",
                f"Exported {len(users)} users to:\n{path}",
            )
        except Exception as e:
            QMessageBox.critical(self._shell, "Error", f"Failed to export:\n{e}")
