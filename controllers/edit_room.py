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


from models.room_model import (
    get_all_rooms,
    create_room,
    update_room,
    delete_room,
)


class EditRoomPage(QWidget):
    """Admin page for managing rooms with CRUD operations, filtering, and CSV support.

    Provides a table view of rooms with inline edit/delete actions,
    status filtering, search, and CSV import/export capabilities.

    Args:
        shell (AdminShellController): The parent admin shell controller.
        preselect_room (dict or None): An optional room dictionary to
            highlight in the table after initialization. Defaults to None.
    """

    def __init__(self, shell, preselect_room=None):
        super().__init__()
        self._shell = shell

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.ui = QWidget()
        uic.loadUi(os.path.join(UI_DIR, "RoomManagement.ui"), self.ui)
        layout.addWidget(self.ui)

        self._connect_signals()
        self._load_table()

        if preselect_room:
            self._preselect(preselect_room)

    def _connect_signals(self):
        """Connect filter buttons, search field, and action buttons to handlers."""
        self.ui.pushButtonAll.clicked.connect(self._apply_filter)
        self.ui.pushButtonAvailable.clicked.connect(self._apply_filter)
        self.ui.pushButtonOccupied.clicked.connect(self._apply_filter)
        self.ui.lineEditSearch.textChanged.connect(self._apply_filter)
        self.ui.pushButtonAdd.clicked.connect(self._add_room)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonExportCSV.clicked.connect(self._export_csv)

    def refresh(self):
        """Reload the rooms table data from the database."""
        self._load_table()

    # -- Table ----------------------------------------------------

    def _load_table(self):
        """Load the rooms table by applying current filters."""
        self._apply_filter()

    def _apply_filter(self):
        """Filter and display rooms based on status filter and search keyword."""
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

    def _populate_table(self, rooms):
        """Populate the rooms table widget with room data and action buttons.

        Args:
            rooms (list[dict]): The list of room dictionaries to display.
        """
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
        """Build a widget containing Edit and Delete buttons for a room row.

        Args:
            room (dict): The room dictionary for the table row.

        Returns:
            QWidget: A container widget with horizontally laid out action buttons.
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        btn_edit = QPushButton()
        btn_edit.setToolTip("Edit")
        btn_edit.setFixedSize(22, 22)
        btn_edit.setIcon(_png_icon("edit.png"))
        btn_edit.setIconSize(QSize(14, 14))
        btn_edit.setStyleSheet(
            "QPushButton{background:#E3F2FD;border:none;border-radius:5px;}"
            "QPushButton:hover{background:#BBDEFB;}"
        )
        btn_edit.clicked.connect(lambda _, r=room: self._edit_room(r))

        btn_del = QPushButton()
        btn_del.setToolTip("Delete")
        btn_del.setFixedSize(22, 22)
        btn_del.setIcon(_png_icon("delete.png"))
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
        """Select and highlight a specific room in the table.

        Args:
            room (dict): The room dictionary containing a 'room_id' key
                to match against the table rows.
        """
        table = self.ui.tableWidget
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == room["room_id"]:
                table.selectRow(row)
                break

    # -- Dialogs --------------------------------------------------

    def _build_room_dialog(self, room=None):
        """Build and configure a dialog for creating or editing a room.

        Args:
            room (dict or None): An existing room record to pre-fill the
                dialog fields. If None, the dialog is configured for creating
                a new room. Defaults to None.

        Returns:
            QDialog: The configured room dialog.
        """
        dlg = QDialog(self._shell)
        uic.loadUi(os.path.join(UI_DIR, "RoomDialog.ui"), dlg)
        if room:
            dlg.setWindowTitle("Edit Room")
            dlg.lblTitle.setText("Edit Room")
            dlg.editId.setText(room["room_id"])
            dlg.editType.setText(room["room_type"])
            dlg.editCap.setText(str(room["capacity"]))
            idx = dlg.comboStatus.findText(room["status"])
            dlg.comboStatus.setCurrentIndex(idx if idx >= 0 else 0)
        dlg.pushButtonCancel.clicked.connect(dlg.reject)
        dlg.pushButtonSave.clicked.connect(dlg.accept)
        return dlg

    def _add_room(self):
        """Open a dialog to create a new room and save it to the database."""
        dlg = self._build_room_dialog()
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        room_id = dlg.editId.text().strip()
        room_type = dlg.editType.text().strip()
        cap_text = dlg.editCap.text().strip()
        status = dlg.comboStatus.currentText()
        if not room_id or not room_type:
            QMessageBox.warning(
                self._shell, "Error", "Please enter Room ID and Room Type."
            )
            return
        try:
            capacity = int(cap_text) if cap_text else 50
        except ValueError:
            QMessageBox.warning(self._shell, "Error", "Capacity must be a number.")
            return
        if create_room(room_id, room_type, capacity, status):
            self._load_table()
        else:
            QMessageBox.warning(self._shell, "Error", "Room ID already exists.")

    def _edit_room(self, room):
        """Open a dialog to edit an existing room.

        Args:
            room (dict): The room dictionary to edit.
        """
        dlg = self._build_room_dialog(room)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        room_id = dlg.editId.text().strip()
        room_type = dlg.editType.text().strip()
        cap_text = dlg.editCap.text().strip()
        status = dlg.comboStatus.currentText()
        if not room_id or not room_type:
            QMessageBox.warning(self._shell, "Error", "Please fill in all fields.")
            return
        try:
            capacity = int(cap_text) if cap_text else 50
        except ValueError:
            QMessageBox.warning(self._shell, "Error", "Capacity must be a number.")
            return
        if update_room(room["id"], room_id, room_type, capacity, status):
            self._load_table()
        else:
            QMessageBox.warning(self._shell, "Error", "Failed to update room.")

    def _delete_room(self, room_pk):
        """Delete a room after user confirmation.

        Args:
            room_pk (int): The primary key of the room to delete.
        """
        reply = QMessageBox.question(self._shell, "Confirm", "Delete this room?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_room(room_pk)
            self._load_table()

    # -- CSV ------------------------------------------------------

    def _import_csv(self):
        """Import rooms from a CSV file into the database.

        Expected CSV columns: room_id, room_type, capacity, status. Displays
        a summary of imported and skipped rows upon completion.
        """
        import csv

        path, _ = QFileDialog.getOpenFileName(
            self._shell, "Open CSV", "", "CSV Files (*.csv)"
        )
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
        """Export all rooms to a CSV file chosen by the user."""
        import csv

        path, _ = QFileDialog.getSaveFileName(
            self._shell,
            "Save CSV",
            "rooms.csv",
            "CSV Files (*.csv)",
        )
        if not path:
            return
        rooms = get_all_rooms()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["room_id", "room_type", "capacity", "status"],
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
                self._shell,
                "Export Complete",
                f"Exported {len(rooms)} rooms to:\n{path}",
            )
        except Exception as e:
            QMessageBox.critical(self._shell, "Error", f"Failed to export:\n{e}")
