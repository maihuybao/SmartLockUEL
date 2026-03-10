from PyQt6.QtWidgets import (
    QTableWidgetItem, QMessageBox, QPushButton, QHeaderView,
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QComboBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from widgets.base_window import BaseWindow
from models.device_model import (
    get_all_devices, search_devices, create_device,
    update_device_password, update_device_status,
    delete_device, generate_password,
)
from models.room_model import get_all_rooms


class DeviceManagementController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Device Management",
        )
        self._selected_device_id = None

        self.ui = self.load_content_ui("DeviceManagement.ui")
        self._connect_signals()
        self._load_table()

    def _connect_sidebar(self):
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(self._go_edit)
        self.sidebar.pushButtonUsers.clicked.connect(self._go_users)
        self.sidebar.pushButtonDevices.clicked.connect(lambda: None)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        self.ui.lineEditSearch.textChanged.connect(self._search)
        self.ui.pushButtonReload.clicked.connect(self._load_table)
        self.ui.pushButtonAdd.clicked.connect(self._add_device)
        self.ui.tableWidgetDevices.cellClicked.connect(self._on_row_click)
        self.ui.pushButtonGenerate.clicked.connect(self._generate_password)
        self.ui.pushButtonConfirm.clicked.connect(self._confirm_password)

    # -- Table ----------------------------------------------------

    def _load_table(self):
        self.ui.lineEditSearch.clear()
        devices = get_all_devices()
        self._populate_table(devices)
        self._clear_detail()

    def _search(self):
        keyword = self.ui.lineEditSearch.text().strip()
        devices = search_devices(keyword) if keyword else get_all_devices()
        self._populate_table(devices)

    def _populate_table(self, devices):
        table = self.ui.tableWidgetDevices
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(4, 70)

        self.ui.lblCount.setText(f"{len(devices)} devices")

        status_colors = {
            "Active": "#4CAF50",
            "Inactive": "#9E9E9E",
            "Maintenance": "#FF9800",
        }

        for row, d in enumerate(devices):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(d["room_name"]))
            table.setItem(row, 1, QTableWidgetItem(d["device_name"]))
            table.setItem(row, 2, QTableWidgetItem(d.get("cabinet_password") or "—"))

            status_item = QTableWidgetItem(d["status"])
            color = status_colors.get(d["status"], "#333")
            status_item.setForeground(QColor(color))
            table.setItem(row, 3, status_item)

            btn_del = QPushButton("Delete")
            btn_del.setFlat(True)
            btn_del.setStyleSheet(
                "QPushButton{background:#F44336;color:white;border:none;font-size:11px;padding:2px 6px;}"
                "QPushButton:hover{background:#C62828;}"
            )
            btn_del.clicked.connect(lambda _, did=d["id"]: self._delete_device(did))
            table.setCellWidget(row, 4, btn_del)

        # Store device list for row click lookup
        self._devices_data = devices

    def _on_row_click(self, row, _col):
        if not hasattr(self, "_devices_data") or row >= len(self._devices_data):
            return
        d = self._devices_data[row]
        self._selected_device_id = d["id"]
        self.ui.lineEditRoom.setText(d["room_name"])
        self.ui.lineEditDevice.setText(d["device_name"])
        self.ui.lineEditNewPassword.clear()

    def _clear_detail(self):
        self._selected_device_id = None
        self.ui.lineEditRoom.clear()
        self.ui.lineEditDevice.clear()
        self.ui.lineEditNewPassword.clear()

    # -- Actions --------------------------------------------------

    def _generate_password(self):
        self.ui.lineEditNewPassword.setText(generate_password())

    def _confirm_password(self):
        if not self._selected_device_id:
            QMessageBox.warning(self, "Error", "Please select a device first.")
            return
        new_pw = self.ui.lineEditNewPassword.text().strip()
        if not new_pw:
            QMessageBox.warning(self, "Error", "Please enter or generate a new password.")
            return
        update_device_password(self._selected_device_id, new_pw)
        QMessageBox.information(self, "Success", f"Password updated to: {new_pw}")
        self._load_table()

    def _delete_device(self, device_id):
        reply = QMessageBox.question(self, "Confirm", "Delete this device?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_device(device_id)
            self._load_table()

    def _add_device(self):
        rooms = get_all_rooms()
        if not rooms:
            QMessageBox.warning(self, "Error", "No rooms available.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Add Device")
        dlg.setMinimumWidth(360)
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

        combo_room = QComboBox()
        for r in rooms:
            combo_room.addItem(f"{r['room_id']} – {r['room_type']}", r["id"])

        edit_name = QLineEdit()
        edit_name.setPlaceholderText("e.g. Smart Lock A1")

        combo_status = QComboBox()
        for s in ("Active", "Inactive", "Maintenance"):
            combo_status.addItem(s)

        form.addRow("Room:", combo_room)
        form.addRow("Device Name:", edit_name)
        form.addRow("Status:", combo_status)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFlat(True)
        btn_cancel.setStyleSheet(
            "QPushButton{background:#F5F5F5;border:1px solid #ddd;border-radius:6px;padding:7px 20px;color:#555;font-size:13px;}"
            "QPushButton:hover{background:#E0E0E0;}"
        )
        btn_ok = QPushButton("Add")
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

        if dlg.exec() == QDialog.DialogCode.Accepted:
            room_id = combo_room.currentData()
            device_name = edit_name.text().strip()
            status = combo_status.currentText()
            if not device_name:
                QMessageBox.warning(self, "Error", "Please enter a device name.")
                return
            if create_device(room_id, device_name, status):
                self._load_table()
            else:
                QMessageBox.warning(self, "Error", "Failed to add device.")
