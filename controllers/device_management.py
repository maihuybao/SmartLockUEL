from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QMessageBox,
    QPushButton,
    QHeaderView,
    QDialog,
    QHBoxLayout,
    QFileDialog,
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


from models.device_model import (
    get_all_devices,
    create_device,
    update_device_password,
    delete_device,
    generate_password,
)
from models.room_model import get_all_rooms


class DeviceManagementPage(QWidget):
    """Admin page for managing devices with CRUD operations and CSV support.

    Provides a table view of devices with inline edit/delete actions,
    status filtering, search, password management, and CSV import/export.

    Args:
        shell (AdminShellController): The parent admin shell controller.
    """

    def __init__(self, shell):
        super().__init__()
        self._shell = shell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.ui = QWidget()
        uic.loadUi(os.path.join(UI_DIR, "DeviceManagement.ui"), self.ui)
        layout.addWidget(self.ui)

        self._connect_signals()
        self._load_table()

    def _connect_signals(self):
        """Connect filter buttons, search field, and action buttons to handlers."""
        self.ui.pushButtonAll.clicked.connect(self._apply_filter)
        self.ui.pushButtonActive.clicked.connect(self._apply_filter)
        self.ui.pushButtonInactive.clicked.connect(self._apply_filter)
        self.ui.pushButtonMaintenance.clicked.connect(self._apply_filter)
        self.ui.lineEditSearch.textChanged.connect(self._apply_filter)
        self.ui.pushButtonAdd.clicked.connect(self._add_device)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    def refresh(self):
        """Reload the devices table data from the database."""
        self._load_table()

    def _load_table(self):
        """Load the devices table by applying current filters."""
        self._apply_filter()

    def _apply_filter(self):
        """Filter and display devices based on status filter and search keyword."""
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
                d
                for d in devices
                if keyword in d["room_name"].lower()
                or keyword in d["device_name"].lower()
            ]
        self._populate_table(devices)

    def _populate_table(self, devices):
        """Populate the devices table widget with device data and action buttons.

        Args:
            devices (list[dict]): The list of device dictionaries to display.
        """
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
            table.setItem(row, 2, QTableWidgetItem(d.get("cabinet_password") or "---"))
            status_item = QTableWidgetItem(d["status"])
            status_item.setForeground(QColor(status_colors.get(d["status"], "#333")))
            table.setItem(row, 3, status_item)
            table.setCellWidget(row, 4, self._make_actions_widget(d))

    def _make_actions_widget(self, device):
        """Build a widget with Edit and Delete buttons for a device row.

        Args:
            device (dict): The device dictionary for the table row.

        Returns:
            QWidget: A container widget with horizontally laid out action buttons.
        """
        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(4)

        btn_edit = QPushButton()
        btn_edit.setToolTip("Edit / Reset Password")
        btn_edit.setFixedSize(22, 22)
        btn_edit.setIcon(_png_icon("edit.png"))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setStyleSheet(
            "QPushButton{background:#E3F2FD;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#BBDEFB;}"
        )
        btn_edit.clicked.connect(lambda _, d=device: self._edit_device(d))

        btn_del = QPushButton()
        btn_del.setToolTip("Delete")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(_png_icon("delete.png"))
        btn_del.setIconSize(QSize(14, 14))
        btn_del.setStyleSheet(
            "QPushButton{background:#FFEBEE;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#FFCDD2;}"
        )
        btn_del.clicked.connect(lambda _, d=device: self._delete_device(d["id"]))

        lay.addWidget(btn_edit)
        lay.addWidget(btn_del)
        lay.addStretch()
        return container

    def _build_device_dialog(self, device=None):
        """Build and configure a dialog for creating or editing a device.

        For editing, includes a password generation button. For creating,
        the password field is hidden.

        Args:
            device (dict or None): An existing device record to pre-fill the
                dialog fields. If None, the dialog is configured for creating
                a new device. Defaults to None.

        Returns:
            QDialog: The configured device dialog.
        """
        rooms = get_all_rooms()
        dlg = QDialog(self._shell)
        uic.loadUi(os.path.join(UI_DIR, "DeviceDialog.ui"), dlg)
        for r in rooms:
            dlg.comboRoom.addItem(f"{r['room_id']} -- {r['room_type']}", r["id"])
        if device:
            dlg.setWindowTitle("Edit Device")
            dlg.lblTitle.setText("Edit Device")
            for i in range(dlg.comboRoom.count()):
                if dlg.comboRoom.itemData(i) == device.get("room_id"):
                    dlg.comboRoom.setCurrentIndex(i)
                    break
            dlg.editName.setText(device["device_name"])
            dlg.comboStatus.setCurrentText(device["status"])
            dlg.btnGenPw.setIcon(_png_icon("refresh.png"))
            dlg.btnGenPw.clicked.connect(
                lambda: dlg.editPw.setText(generate_password())
            )
        else:
            dlg.labelPw.setVisible(False)
            dlg.pwWidget.setVisible(False)
        dlg.pushButtonCancel.clicked.connect(dlg.reject)
        dlg.pushButtonSave.clicked.connect(dlg.accept)
        return dlg

    def _add_device(self):
        """Open a dialog to create a new device and save it to the database."""
        dlg = self._build_device_dialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        room_id = dlg.comboRoom.currentData()
        device_name = dlg.editName.text().strip()
        status = dlg.comboStatus.currentText()
        if not device_name:
            QMessageBox.warning(self._shell, "Error", "Please enter a device name.")
            return
        if create_device(room_id, device_name, status):
            self._load_table()
        else:
            QMessageBox.warning(self._shell, "Error", "Failed to add device.")

    def _edit_device(self, device):
        """Open a dialog to edit a device, including status and optional password reset.

        Args:
            device (dict): The device dictionary to edit.
        """
        dlg = self._build_device_dialog(device)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        device_name = dlg.editName.text().strip()
        status = dlg.comboStatus.currentText()
        new_pw = dlg.editPw.text().strip()
        if not device_name:
            QMessageBox.warning(self._shell, "Error", "Please enter a device name.")
            return
        from models.device_model import update_device_status

        update_device_status(device["id"], status)
        if new_pw:
            update_device_password(device["id"], new_pw)
        self._load_table()

    def _delete_device(self, device_id):
        """Delete a device after user confirmation.

        Args:
            device_id (int): The primary key of the device to delete.
        """
        reply = QMessageBox.question(self._shell, "Confirm", "Delete this device?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_device(device_id)
            self._load_table()

    def _import_csv(self):
        """Import devices from a CSV file into the database.

        Expected CSV columns: room_id, device_name, status. Displays a summary
        of imported and skipped rows upon completion.
        """
        import csv

        path, _ = QFileDialog.getOpenFileName(
            self._shell, "Open CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return
        imported, skipped, errors = 0, 0, []
        rooms = {r["room_id"]: r["id"] for r in get_all_rooms()}
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                for i, row in enumerate(csv.DictReader(f), start=2):
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
        """Export all devices to a CSV file chosen by the user."""
        import csv

        path, _ = QFileDialog.getSaveFileName(
            self._shell, "Save CSV", "devices.csv", "CSV Files (*.csv)"
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
                    writer.writerow(
                        {
                            "room": d["room_name"],
                            "device_name": d["device_name"],
                            "cabinet_password": d.get("cabinet_password") or "",
                            "status": d["status"],
                        }
                    )
            QMessageBox.information(
                self._shell,
                "Export Complete",
                f"Exported {len(devices)} devices to:\n{path}",
            )
        except Exception as e:
            QMessageBox.critical(self._shell, "Error", f"Failed to export:\n{e}")
