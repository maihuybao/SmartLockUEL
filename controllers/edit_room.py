from PyQt6.QtWidgets import (
    QTableWidgetItem, QMessageBox, QApplication, QHeaderView,
)

from widgets.base_window import BaseWindow
from models.room_model import (
    get_all_rooms, search_rooms, create_room, update_room, delete_room,
)


class EditRoomController(BaseWindow):
    def __init__(self, user):
        super().__init__(
            user, role_text="Admin", show_search=False,
            show_sidebar=True, title="SmartLocker UEL - Edit Rooms",
        )
        self._selected_pk = None

        # Load content from .ui
        self.ui = self.load_content_ui("Edit.ui")

        self._connect_signals()
        self._load_table()

    def _connect_sidebar(self):
        """Override: Edit is current page."""
        self.sidebar.btnOverview.clicked.connect(self._go_overview)
        self.sidebar.btnEdit.clicked.connect(lambda: None)
        self.sidebar.btnUsers.clicked.connect(self._go_users)
        self.sidebar.btnLogout.clicked.connect(self._logout)
        self.sidebar.btnQuit.clicked.connect(QApplication.quit)

    def _connect_signals(self):
        self.ui.btnCreate.clicked.connect(self._create)
        self.ui.btnUpdate.clicked.connect(self._update)
        self.ui.btnDelete.clicked.connect(self._delete)
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
        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        self.ui.LineEditStatus.setText(self.ui.tableWidget.item(row, 3).text())
        room_id = self.ui.tableWidget.item(row, 0).text()
        rooms = get_all_rooms()
        match = [r for r in rooms if r["room_id"] == room_id]
        self._selected_pk = match[0]["id"] if match else None

    def _clear_form(self):
        self.ui.LineEditRoomID.clear()
        self.ui.LineEditRoomType.clear()
        self.ui.LineEditStatus.clear()
        self._selected_pk = None

    # ── CRUD ─────────────────────────────────────────────

    def _create(self):
        room_id = self.ui.LineEditRoomID.text().strip()
        room_type = self.ui.LineEditRoomType.text().strip()
        status = self.ui.LineEditStatus.text().strip() or "Available"
        if not room_id or not room_type:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Room ID và Room Type.")
            return
        if create_room(room_id, room_type, 50, status):
            QMessageBox.information(self, "Thành công", "Đã tạo phòng mới.")
            self._load_table()
        else:
            QMessageBox.warning(self, "Lỗi", "Room ID đã tồn tại.")

    def _update(self):
        if not self._selected_pk:
            QMessageBox.warning(self, "Lỗi", "Chọn phòng cần cập nhật.")
            return
        room_id = self.ui.LineEditRoomID.text().strip()
        room_type = self.ui.LineEditRoomType.text().strip()
        status = self.ui.LineEditStatus.text().strip()
        if not room_id or not room_type or not status:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        if update_room(self._selected_pk, room_id, room_type, 50, status):
            QMessageBox.information(self, "Thành công", "Đã cập nhật phòng.")
            self._load_table()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể cập nhật.")

    def _delete(self):
        if not self._selected_pk:
            QMessageBox.warning(self, "Lỗi", "Chọn phòng cần xóa.")
            return
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa phòng này?")
        if reply == QMessageBox.StandardButton.Yes:
            delete_room(self._selected_pk)
            QMessageBox.information(self, "Thành công", "Đã xóa phòng.")
            self._load_table()
