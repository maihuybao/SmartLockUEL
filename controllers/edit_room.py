from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QFileDialog,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QComboBox,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
import os
import re

from widgets.base_window import BaseWindow
from models.room_model import (
    get_all_rooms,
    create_room,
    update_room,
    delete_room,
)

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


class EditRoomController(BaseWindow):
    def __init__(self, user, preselect_room=None):
        super().__init__(
            user,
            role_text="Admin",
            show_search=False,
            show_sidebar=True,
            title="SmartLocker UEL - Edit Rooms",
        )
        self.ui = self.load_content_ui("RoomManagement.ui")
        self._connect_signals()
        self._load_table()

        if preselect_room:
            self._preselect(preselect_room)

    def _connect_sidebar(self):
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(lambda: None)
        self.sidebar.pushButtonUsers.clicked.connect(self._go_users)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        self.ui.pushButtonAll.clicked.connect(self._apply_filter)
        self.ui.pushButtonAvailable.clicked.connect(self._apply_filter)
        self.ui.pushButtonOccupied.clicked.connect(self._apply_filter)
        self.ui.lineEditSearch.textChanged.connect(self._apply_filter)
        self.ui.pushButtonAdd.clicked.connect(self._add_room)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    # -- Table ----------------------------------------------------

    def _load_table(self):
        self._apply_filter()

    def _apply_filter(self):
        rooms = get_all_rooms()

        if self.ui.pushButtonAvailable.isChecked():
            rooms = [r for r in rooms if r["status"] == "Available"]
        elif self.ui.pushButtonOccupied.isChecked():
            rooms = [r for r in rooms if r["status"] == "Occupied"]

        keyword = self.ui.lineEditSearch.text().strip().lower()
        if keyword:
            rooms = [
                r
                for r in rooms
                if keyword in r["room_id"].lower() or keyword in r["room_type"].lower()
            ]

        self._populate_table(rooms)

    def _search(self):
        self._apply_filter()

    def _populate_table(self, rooms):
        table = self.ui.tableWidget
        table.setRowCount(0)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(4, 72)
        table.verticalHeader().setDefaultSectionSize(32)

        self.ui.lblCount.setText(f"{len(rooms)} rooms")

        status_colors = {
            "Available": "#4CAF50",
            "Occupied": "#FF9800",
            "Cleaning": "#2196F3",
            "Full": "#F44336",
        }

        for row, room in enumerate(rooms):
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(room["room_id"]))
            table.setItem(row, 1, QTableWidgetItem(room["room_type"]))
            table.setItem(row, 2, QTableWidgetItem(str(room["capacity"])))

            status_item = QTableWidgetItem(room["status"])
            status_item.setForeground(QColor(status_colors.get(room["status"], "#333")))
            table.setItem(row, 3, status_item)

            table.setCellWidget(row, 4, self._make_actions_widget(room))

        self._rooms_data = rooms

    def _make_actions_widget(self, room):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        btn_edit = QPushButton()
        btn_edit.setToolTip("Edit")
        btn_edit.setFixedSize(22, 22)
        btn_edit.setIcon(_svg_icon("edit.svg", "#1565C0"))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setStyleSheet(
            "QPushButton{background:#E3F2FD;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#BBDEFB;}"
        )
        btn_edit.clicked.connect(lambda _, r=room: self._edit_room(r))

        btn_del = QPushButton()
        btn_del.setToolTip("Delete")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(_svg_icon("delete.svg", "#C62828"))
        btn_del.setIconSize(QSize(14, 14))
        btn_del.setStyleSheet(
            "QPushButton{background:#FFEBEE;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#FFCDD2;}"
        )
        btn_del.clicked.connect(lambda _, r=room: self._delete_room(r["id"]))

        layout.addWidget(btn_edit)
        layout.addWidget(btn_del)
        layout.addStretch()
        return container

    def _preselect(self, room):
        table = self.ui.tableWidget
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == room["room_id"]:
                table.selectRow(row)
                break

    # -- Dialogs --------------------------------------------------

    def _build_room_dialog(self, room=None):
        dlg = QDialog(self)
        dlg.setWindowTitle("Add Room" if not room else "Edit Room")
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

        edit_id = QLineEdit()
        edit_id.setPlaceholderText("e.g. P101")
        edit_type = QLineEdit()
        edit_type.setPlaceholderText("e.g. Study Room")
        edit_cap = QLineEdit()
        edit_cap.setPlaceholderText("e.g. 10")
        combo_status = QComboBox()
        for s in ("Available", "Occupied", "Cleaning"):
            combo_status.addItem(s)

        if room:
            edit_id.setText(room["room_id"])
            edit_type.setText(room["room_type"])
            edit_cap.setText(str(room["capacity"]))
            idx = combo_status.findText(room["status"])
            combo_status.setCurrentIndex(idx if idx >= 0 else 0)

        form.addRow("Room ID:", edit_id)
        form.addRow("Room Type:", edit_type)
        form.addRow("Capacity:", edit_cap)
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

        dlg.editId = edit_id
        dlg.editType = edit_type
        dlg.editCap = edit_cap
        dlg.comboStatus = combo_status
        return dlg

    def _add_room(self):
        dlg = self._build_room_dialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        room_id = dlg.editId.text().strip()
        room_type = dlg.editType.text().strip()
        cap_text = dlg.editCap.text().strip()
        status = dlg.comboStatus.currentText()
        if not room_id or not room_type:
            QMessageBox.warning(self, "Error", "Please enter Room ID and Room Type.")
            return
        try:
            capacity = int(cap_text) if cap_text else 50
        except ValueError:
            QMessageBox.warning(self, "Error", "Capacity must be a number.")
            return
        if create_room(room_id, room_type, capacity, status):
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Room ID already exists.")

    def _edit_room(self, room):
        dlg = self._build_room_dialog(room)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        room_id = dlg.editId.text().strip()
        room_type = dlg.editType.text().strip()
        cap_text = dlg.editCap.text().strip()
        status = dlg.comboStatus.currentText()
        if not room_id or not room_type:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        try:
            capacity = int(cap_text) if cap_text else 50
        except ValueError:
            QMessageBox.warning(self, "Error", "Capacity must be a number.")
            return
        if update_room(room["id"], room_id, room_type, capacity, status):
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to update room.")

    def _delete_room(self, room_pk):
        reply = QMessageBox.question(self, "Confirm", "Delete this room?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_room(room_pk)
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
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):
                    room_id = (row.get("room_id") or "").strip()
                    room_type = (row.get("room_type") or "").strip()
                    capacity_raw = (row.get("capacity") or "50").strip()
                    status = (row.get("status") or "Available").strip()
                    if not room_id or not room_type:
                        errors.append(f"Row {i}: missing room_id or room_type")
                        skipped += 1
                        continue
                    try:
                        capacity = int(capacity_raw)
                    except ValueError:
                        errors.append(f"Row {i}: invalid capacity '{capacity_raw}'")
                        skipped += 1
                        continue
                    if create_room(room_id, room_type, capacity, status):
                        imported += 1
                    else:
                        errors.append(f"Row {i}: room_id '{room_id}' already exists")
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
            self, "Save CSV", "rooms.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        rooms = get_all_rooms()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f, fieldnames=["room_id", "room_type", "capacity", "status"]
                )
                writer.writeheader()
                for r in rooms:
                    writer.writerow(
                        {
                            "room_id": r["room_id"],
                            "room_type": r["room_type"],
                            "capacity": r["capacity"],
                            "status": r["status"],
                        }
                    )
            QMessageBox.information(
                self, "Export Complete", f"Exported {len(rooms)} rooms to:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")
