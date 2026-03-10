from PyQt6.QtWidgets import (
    QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog,
    QPushButton, QHBoxLayout, QWidget, QDialog, QVBoxLayout,
    QFormLayout, QLineEdit, QComboBox, QLabel,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
import os, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def _svg_icon(name, color, size=16):
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
from models.user_model import get_all_users, create_user, update_user, delete_user


class UsersManagementController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Users Management",
        )
        self.ui = self.load_content_ui("Users.ui")
        self._connect_signals()
        self._load_table()

    def _connect_sidebar(self):
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(self._go_edit)
        self.sidebar.pushButtonUsers.clicked.connect(lambda: None)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        self.ui.pushButtonAll.clicked.connect(self._apply_filter)
        self.ui.pushButtonAdmin.clicked.connect(self._apply_filter)
        self.ui.pushButtonUser.clicked.connect(self._apply_filter)
        self.ui.lineEditSearch.textChanged.connect(self._apply_filter)
        self.ui.pushButtonAdd.clicked.connect(self._add_user)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    # -- Table ----------------------------------------------------

    def _load_table(self):
        self._apply_filter()

    def _apply_filter(self):
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

        self._users_data = users

    def _make_actions_widget(self, user):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        btn_view = QPushButton()
        btn_view.setToolTip("View Bookings")
        btn_view.setFixedSize(22, 22)
        btn_view.setIcon(_svg_icon("view.svg", "#6A1B9A"))
        btn_view.setIconSize(QSize(14, 14))
        btn_view.setStyleSheet(
            "QPushButton{background:#F3E5F5;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#E1BEE7;}"
        )
        btn_view.clicked.connect(lambda _, u=user: self._view_user_bookings(u))

        btn_edit = QPushButton()
        btn_edit.setToolTip("Edit")
        btn_edit.setFixedSize(22, 22)
        btn_edit.setIcon(_svg_icon("edit.svg", "#1565C0"))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setStyleSheet(
            "QPushButton{background:#E3F2FD;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#BBDEFB;}"
        )
        btn_edit.clicked.connect(lambda _, u=user: self._edit_user(u))

        btn_del = QPushButton()
        btn_del.setToolTip("Delete")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(_svg_icon("delete.svg", "#C62828"))
        btn_del.setIconSize(QSize(14, 14))
        btn_del.setStyleSheet(
            "QPushButton{background:#FFEBEE;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#FFCDD2;}"
        )
        btn_del.clicked.connect(lambda _, u=user: self._delete_user(u["id"]))

        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        layout.addStretch()
        return container

    # -- Dialogs --------------------------------------------------

    def _build_user_dialog(self, user=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add User" if not user else "Edit User")
        dlg.setMinimumWidth(360)
        dlg.setStyleSheet(
            "QDialog { background: white; }"
            "QLabel { color: #333; font-size: 13px; }"
            "QComboBox, QLineEdit { padding: 6px; border: 1px solid #ddd; border-radius: 6px;"
            " color: #333; font-size: 13px; background: white; }"
            "QComboBox:focus, QLineEdit:focus { border: 1px solid #1F4F82; }"
        )
        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        edit_username = QLineEdit()
        edit_username.setPlaceholderText("Username")
        edit_password = QLineEdit()
        edit_password.setPlaceholderText("Password (leave blank to keep)")
        edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        combo_role = QComboBox()
        combo_role.addItems(["user", "admin"])

        if user:
            edit_username.setText(user["username"])
            combo_role.setCurrentText(user["role"])

        form.addRow("Username:", edit_username)
        form.addRow("Password:", edit_password)
        form.addRow("Role:", combo_role)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFlat(True)
        btn_cancel.setStyleSheet(
            "QPushButton{background:#F5F5F5;border:1px solid #ddd;border-radius:6px;"
            "padding:7px 20px;color:#555;font-size:13px;}"
            "QPushButton:hover{background:#E0E0E0;}"
        )
        btn_ok = QPushButton("Save")
        btn_ok.setFlat(True)
        btn_ok.setStyleSheet(
            "QPushButton{background:#1F4F82;border:none;border-radius:6px;"
            "padding:7px 20px;color:white;font-size:13px;font-weight:bold;}"
            "QPushButton:hover{background:#163D66;}"
        )
        btn_cancel.clicked.connect(dlg.reject)
        btn_ok.clicked.connect(dlg.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        dlg.editUsername = edit_username
        dlg.editPassword = edit_password
        dlg.comboRole = combo_role
        return dlg

    def _add_user(self):
        dlg = self._build_user_dialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        username = dlg.editUsername.text().strip()
        password = dlg.editPassword.text().strip()
        role = dlg.comboRole.currentText()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return
        if create_user(username, password, role):
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Username already exists.")

    def _edit_user(self, user):
        dlg = self._build_user_dialog(user)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        username = dlg.editUsername.text().strip()
        password = dlg.editPassword.text().strip()
        role = dlg.comboRole.currentText()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return
        if update_user(user["id"], username, password, role):
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to update user.")

    def _delete_user(self, user_id):
        if user_id == self.current_user["id"]:
            QMessageBox.warning(self, "Error", "You cannot delete your own account.")
            return
        reply = QMessageBox.question(self, "Confirm", "Delete this user?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_user(user_id)
            self._load_table()

    def _view_user_bookings(self, user):
        from models.booking_model import get_bookings_by_user

        bookings = get_bookings_by_user(user["id"])

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Bookings — {user['username']}")
        dlg.setMinimumSize(700, 420)
        dlg.setStyleSheet("QDialog { background: white; }")

        layout = QVBoxLayout(dlg)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 16)

        header = QLabel(f"Booking history: {user['username']}")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            "QLabel { background: #1F4F82; color: white; font-size: 15px;"
            " font-weight: bold; padding: 14px; }"
        )
        layout.addWidget(header)

        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            ["Room", "Type", "Date", "Start", "End", "Purpose", "Status"]
        )
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(30)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setStyleSheet(
            "QTableWidget { background: white; color: #333; border: none; font-size: 13px; }"
            "QTableWidget::item { padding: 4px; }"
            "QTableWidget::item:selected { background: #BBDEFB; color: #333; }"
            "QHeaderView::section { background: #1F4F82; color: white; font-weight: bold;"
            " padding: 6px; border: none; }"
        )

        status_colors = {"Pending": "#FF9800", "Approved": "#4CAF50", "Rejected": "#F44336"}

        table.setRowCount(len(bookings))
        for row, b in enumerate(bookings):
            session = b.get("session", "")
            date, start, end = ("", "", "")
            if " | " in session:
                date, tp = session.split(" | ", 1)
                if " - " in tp:
                    start, end = tp.split(" - ", 1)
            table.setItem(row, 0, QTableWidgetItem(b["room_name"]))
            table.setItem(row, 1, QTableWidgetItem(b["room_type"]))
            table.setItem(row, 2, QTableWidgetItem(date.strip()))
            table.setItem(row, 3, QTableWidgetItem(start.strip()))
            table.setItem(row, 4, QTableWidgetItem(end.strip()))
            table.setItem(row, 5, QTableWidgetItem(b.get("reason", "")))
            status_item = QTableWidgetItem(b["status"])
            status_item.setForeground(QColor(status_colors.get(b["status"], "#333")))
            table.setItem(row, 6, status_item)

        layout.addWidget(table)

        lbl_count = QLabel(f"{len(bookings)} bookings")
        lbl_count.setStyleSheet("color: #888; font-size: 12px; padding: 6px 16px 0;")
        layout.addWidget(lbl_count)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(16, 8, 16, 0)
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

    # -- CSV ------------------------------------------------------

    def _import_csv(self):
        import csv

        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        imported = 0
        skipped = 0
        errors = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):
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

        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "users.csv", "CSV Files (*.csv)")
        if not path:
            return
        users = get_all_users()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["username", "role"])
                writer.writeheader()
                for u in users:
                    writer.writerow({"username": u["username"], "role": u["role"]})
            QMessageBox.information(self, "Export Complete", f"Exported {len(users)} users to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")
