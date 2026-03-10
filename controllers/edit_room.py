from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QMessageBox,
    QApplication,
    QHeaderView,
    QFileDialog,
)

from widgets.base_window import BaseWindow
from models.room_model import (
    get_all_rooms,
    search_rooms,
    create_room,
    update_room,
    delete_room,
)


class EditRoomController(BaseWindow):
    def __init__(self, user, preselect_room=None):
        super().__init__(
            user,
            role_text="Admin",
            show_search=False,
            show_sidebar=True,
            title="SmartLocker UEL - Edit Rooms",
        )
        self._selected_pk = None

        # Load content from .ui
        self.ui = self.load_content_ui("RoomManagement.ui")

        self._connect_signals()
        self._load_table()

        if preselect_room:
            self._preselect(preselect_room)

    def _connect_sidebar(self):
        """Override: Edit is current page."""
        self.sidebar.pushButtonOverview.clicked.connect(self._go_overview)
        self.sidebar.pushButtonBookings.clicked.connect(self._go_bookings)
        self.sidebar.pushButtonEdit.clicked.connect(lambda: None)
        self.sidebar.pushButtonUsers.clicked.connect(self._go_users)
        self.sidebar.pushButtonDevices.clicked.connect(self._go_devices)
        self.sidebar.pushButtonLogOut.clicked.connect(self._logout)
        self.sidebar.pushButtonQuit.clicked.connect(self._quit)

    def _connect_signals(self):
        self.ui.pushButtonCreate.clicked.connect(self._create)
        self.ui.pushButtonUpdate.clicked.connect(self._update)
        self.ui.pushButtonDelete.clicked.connect(self._delete)
        self.ui.pushButtonImportCSV.clicked.connect(self._import_csv)
        self.ui.pushButtonReload.clicked.connect(self._load_table)
        self.ui.lineEditSearch.returnPressed.connect(self._search)
        self.ui.lineEditSearch.textChanged.connect(self._search)
        self.ui.tableWidget.cellClicked.connect(self._on_row_click)

    # ── Table ────────────────────────────────────────────

    def _load_table(self):
        rooms = get_all_rooms()
        self._populate_table(rooms)
        self._clear_form()

    def _search(self):
        keyword = self.ui.lineEditSearch.text().strip()
        rooms = search_rooms(keyword) if keyword else get_all_rooms()
        self._populate_table(rooms)

    def _populate_table(self, rooms):
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        for room in rooms:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(room["room_id"]))
            self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(room["room_type"]))
            self.ui.tableWidget.setItem(row, 2, QTableWidgetItem(str(room["capacity"])))
            self.ui.tableWidget.setItem(row, 3, QTableWidgetItem(room["status"]))

    def _on_row_click(self, row, _col):
        self.ui.LineEditRoomID.setText(self.ui.tableWidget.item(row, 0).text())
        self.ui.LineEditRoomType.setText(self.ui.tableWidget.item(row, 1).text())
        self.ui.LineEditCapacity.setText(self.ui.tableWidget.item(row, 2).text())
        status = self.ui.tableWidget.item(row, 3).text()
        idx = self.ui.comboBoxStatus.findText(status)
        self.ui.comboBoxStatus.setCurrentIndex(idx if idx >= 0 else 0)
        room_id = self.ui.tableWidget.item(row, 0).text()
        rooms = get_all_rooms()
        match = [r for r in rooms if r["room_id"] == room_id]
        self._selected_pk = match[0]["id"] if match else None

    def _clear_form(self):
        self.ui.LineEditRoomID.clear()
        self.ui.LineEditRoomType.clear()
        self.ui.LineEditCapacity.clear()
        self.ui.comboBoxStatus.setCurrentIndex(0)
        self._selected_pk = None

    def _preselect(self, room):
        self._selected_pk = room["id"]
        self.ui.LineEditRoomID.setText(room["room_id"])
        self.ui.LineEditRoomType.setText(room["room_type"])
        self.ui.LineEditCapacity.setText(str(room.get("capacity", "")))
        idx = self.ui.comboBoxStatus.findText(room["status"])
        self.ui.comboBoxStatus.setCurrentIndex(idx if idx >= 0 else 0)
        # Highlight row trong table
        table = self.ui.tableWidget
        for row in range(table.rowCount()):
            if table.item(row, 0) and table.item(row, 0).text() == room["room_id"]:
                table.selectRow(row)
                break

    # ── CRUD ─────────────────────────────────────────────

    def _create(self):
        room_id = self.ui.LineEditRoomID.text().strip()
        room_type = self.ui.LineEditRoomType.text().strip()
        capacity_text = self.ui.LineEditCapacity.text().strip()
        status = self.ui.comboBoxStatus.currentText()
        if not room_id or not room_type:
            QMessageBox.warning(self, "Error", "Please enter Room ID and Room Type.")
            return
        try:
            capacity = int(capacity_text) if capacity_text else 50
        except ValueError:
            QMessageBox.warning(self, "Error", "Capacity must be a number.")
            return
        if create_room(room_id, room_type, capacity, status):
            QMessageBox.information(self, "Success", "Room created successfully.")
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Room ID already exists.")

    def _update(self):
        if not self._selected_pk:
            QMessageBox.warning(self, "Error", "Please select a room to update.")
            return
        room_id = self.ui.LineEditRoomID.text().strip()
        room_type = self.ui.LineEditRoomType.text().strip()
        capacity_text = self.ui.LineEditCapacity.text().strip()
        status = self.ui.comboBoxStatus.currentText()
        if not room_id or not room_type:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        try:
            capacity = int(capacity_text) if capacity_text else 50
        except ValueError:
            QMessageBox.warning(self, "Error", "Capacity must be a number.")
            return
        if update_room(self._selected_pk, room_id, room_type, capacity, status):
            QMessageBox.information(self, "Success", "Room updated successfully.")
            self._load_table()
        else:
            QMessageBox.warning(self, "Error", "Failed to update room.")

    def _delete(self):
        if not self._selected_pk:
            QMessageBox.warning(self, "Error", "Please select a room to delete.")
            return
        reply = QMessageBox.question(
            self, "Confirm", "Are you sure you want to delete this room?"
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_room(self._selected_pk)
            QMessageBox.information(self, "Success", "Room deleted successfully.")
            self._load_table()

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
