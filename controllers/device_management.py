from PyQt6.QtWidgets import (
    QTableWidgetItem, QMessageBox, QPushButton, QHeaderView,
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit,
    QComboBox, QFileDialog, QWidget, QLabel,
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
from models.device_model import (
    get_all_devices,
    search_devices,
    create_device,
    update_device_password,
    delete_device,
    generate_password,
)
from models.room_model import get_all_rooms


class DeviceManagementController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Device Management",
        )
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
        self.ui.pushButtonAll.clicked.connect(self._apply_filter)
        self.ui.pushButtonActive.clicked.connect(self._apply_filter)
        self.ui.pushButtonInactive.clicked.connect(self._apply_filter)
        self.ui.pushButtonMaintenance.clicked.connect(self._apply_filter)
        self.ui.lineEditSearch.textChanged.connect(self._apply_filter)
        self.ui.pushButtonAdd.clicked.connect(self._add_device)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    # -- Table ----------------------------------------------------

    def _load_table(self):
        self._apply_filter()

    def _apply_filter(self):
        devices = get_all_devices()

        if self.ui.pushButtonActive.isChecked():
            devices = [d for d in devices if d["status"] == "Active"]
        elif self.ui.pushButtonInactive.isChecked():
            devices = [d for d in devices if d["status"] == "Inactive"]
        elif self.ui.pushButtonMaintenance.isChecked():
            devices = [d for d in devices if d["status"] == "Maintenance"]

        keyword = self.ui.lineEditSearch.text().strip().lower()
        if keyword:
            devices = [
                d for d in devices
                if keyword in d["room_name"].lower()
                or keyword in d["device_name"].lower()
            ]

        self._populate_table(devices)

    def _populate_table(self, devices):
        table = self.ui.tableWidgetDevices
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(4, 100)
        table.verticalHeader().setDefaultSectionSize(32)

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
            status_item.setForeground(QColor(status_colors.get(d["status"], "#333")))
            table.setItem(row, 3, status_item)

            table.setCellWidget(row, 4, self._make_actions_widget(d))

        self._devices_data = devices

    def _make_actions_widget(self, device):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        btn_edit = QPushButton()
        btn_edit.setToolTip("Edit / Reset Password")
        btn_edit.setFixedSize(22, 22)
        btn_edit.setIcon(_svg_icon("edit.svg", "#1565C0"))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setStyleSheet(
            "QPushButton{background:#E3F2FD;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#BBDEFB;}"
        )
        btn_edit.clicked.connect(lambda _, d=device: self._edit_device(d))

        btn_del = QPushButton()
        btn_del.setToolTip("Delete")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(_svg_icon("delete.svg", "#C62828"))
        btn_del.setIconSize(QSize(14, 14))
        btn_del.setStyleSheet(
            "QPushButton{background:#FFEBEE;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#FFCDD2;}"
        )
        btn_del.clicked.connect(lambda _, d=device: self._delete_device(d["id"]))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        layout.addStretch()
        return container

    # -- Dialogs --------------------------------------------------

    def _build_device_dialog(self, device=None):
        rooms = get_all_rooms()
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Device" if not device else "Edit Device")
        dlg.setMinimumWidth(380)
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

        combo_room = QComboBox()
        for r in rooms:
            combo_room.addItem(f"{r['room_id']} – {r['room_type']}", r["id"])

        edit_name = QLineEdit()
        edit_name.setPlaceholderText("e.g. Smart Lock A1")

        combo_status = QComboBox()
        combo_status.addItems(["Active", "Inactive", "Maintenance"])

        edit_pw = QLineEdit()
        edit_pw.setPlaceholderText("Leave blank to keep current")

        if device:
            for i in range(combo_room.count()):
                if combo_room.itemData(i) == device.get("room_id"):
                    combo_room.setCurrentIndex(i)
                    break
            edit_name.setText(device["device_name"])
            combo_status.setCurrentText(device["status"])

        form.addRow("Room:", combo_room)
        form.addRow("Device Name:", edit_name)
        form.addRow("Status:", combo_status)
        if device:
            pw_widget = QWidget()
            pw_row = QHBoxLayout(pw_widget)
            pw_row.setContentsMargins(0, 0, 0, 0)
            pw_row.setSpacing(4)
            pw_row.addWidget(edit_pw)

            btn_gen = QPushButton()
            btn_gen.setFixedSize(28, 28)
            btn_gen.setIcon(_svg_icon("refresh.svg", "#F57F17"))
            btn_gen.setIconSize(QSize(16, 16))
            btn_gen.setToolTip("Generate password")
            btn_gen.setStyleSheet(
                "QPushButton{background:#FFF8E1;border:1px solid #F9A825;border-radius:6px;}"
                "QPushButton:hover{background:#FBC02D;}"
            )
            btn_gen.clicked.connect(lambda: edit_pw.setText(generate_password()))
            pw_row.addWidget(btn_gen)

            form.addRow("New Password:", pw_widget)

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

        dlg.comboRoom = combo_room
        dlg.editName = edit_name
        dlg.comboStatus = combo_status
        dlg.editPw = edit_pw if device else None
        return dlg

    def _add_device(self):
        dlg = self._build_device_dialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        room_id = dlg.comboRoom.currentData()
        device_name = dlg.editName.text().strip()
        status = dlg.comboStatus.currentText()
        if not device_name:
            QMessageBox.warning(self, "Error", "Please enter a device name.")
            return
        if create_device(room_id, device_name, status):
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to add device.")

    def _edit_device(self, device):
        dlg = self._build_device_dialog(device)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        device_name = dlg.editName.text().strip()
        status = dlg.comboStatus.currentText()
        new_pw = dlg.editPw.text().strip() if dlg.editPw else ""
        if not device_name:
            QMessageBox.warning(self, "Error", "Please enter a device name.")
            return
        from models.device_model import update_device_status
        update_device_status(device["id"], status)
        if new_pw:
            update_device_password(device["id"], new_pw)
        self._load_table()

    def _delete_device(self, device_id):
        reply = QMessageBox.question(self, "Confirm", "Delete this device?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_device(device_id)
            self._load_table()

    # -- CSV ------------------------------------------------------

    def _import_csv(self):
        import csv

        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        imported = 0
        skipped = 0
        errors = []
        rooms = {r["room_id"]: r["id"] for r in get_all_rooms()}
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):
                    room_id_str = (row.get("room_id") or "").strip()
                    device_name = (row.get("device_name") or "").strip()
                    status = (row.get("status") or "Active").strip()
                    if not room_id_str or not device_name:
                        errors.append(f"Row {i}: missing room_id or device_name")
                        skipped += 1
                        continue
                    room_pk = rooms.get(room_id_str)
                    if not room_pk:
                        errors.append(f"Row {i}: room_id '{room_id_str}' not found")
                        skipped += 1
                        continue
                    if create_device(room_pk, device_name, status):
                        imported += 1
                    else:
                        errors.append(f"Row {i}: failed to create '{device_name}'")
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

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "devices.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        devices = get_all_devices()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["room", "device_name", "cabinet_password", "status"]
                )
                writer.writeheader()
                for d in devices:
                    writer.writerow({
                        "room": d["room_name"],
                        "device_name": d["device_name"],
                        "cabinet_password": d.get("cabinet_password") or "",
                        "status": d["status"],
                    })
            QMessageBox.information(
                self, "Export Complete", f"Exported {len(devices)} devices to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")
