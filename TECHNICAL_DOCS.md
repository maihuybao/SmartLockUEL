# SmartLocker UEL — Tài liệu Kỹ thuật

**Phiên bản:** 3.0
**Ngày:** 2026-03-10
**Nền tảng:** Python 3.10+, PyQt6, SQLite 3

---

## 1. Tổng quan Dự án

### 1.1 Mục đích

SmartLocker UEL là ứng dụng desktop dùng để quản lý đặt phòng và thiết bị tủ khóa thông minh tại Trường Đại học Kinh tế Luật (UEL). Ứng dụng số hóa quy trình đặt phòng, cho phép sinh viên và giảng viên đặt phòng trực tuyến, trong khi quản trị viên xử lý duyệt yêu cầu, quản lý danh sách phòng, tài khoản người dùng và thiết bị tủ khóa.

### 1.2 Phạm vi

| Vai trò | Khả năng |
|---|---|
| Admin | Xem lưới phòng với thống kê dashboard, quản lý booking (duyệt/từ chối/CRUD + import/export CSV), quản lý phòng (CRUD + CSV), quản lý tài khoản (CRUD + CSV + xem lịch sử booking của từng user), quản lý thiết bị (CRUD + CSV + sinh mật khẩu) |
| User | Xem phòng khả dụng với 3 nhóm filter (trạng thái/sức chứa/ca học), gửi yêu cầu đặt phòng kèm bảng availability, xem lịch sử booking, chỉnh sửa/hủy booking đang Pending, xem chi tiết booking |

### 1.3 Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ lập trình | Python 3.10+ |
| Framework GUI | PyQt6 |
| Thiết kế giao diện | Qt Designer (file .ui), nạp qua `PyQt6.uic.loadUi()` |
| Cơ sở dữ liệu | SQLite 3 — file tại `datasets/smartlocker.db` |
| Băm mật khẩu | SHA-256 qua `hashlib` |
| Biểu tượng | File PNG (15 file trong `images/`) |
| Import/Export dữ liệu | CSV qua module `csv` của thư viện chuẩn Python |

### 1.4 Cấu trúc Dự án

```
SmartLockUEL/
├── main.py                    # Điểm khởi động ứng dụng
├── database.py                # Kết nối SQLite, khởi tạo schema
├── seed.py                    # Reset DB và tạo dữ liệu mẫu
├── CLAUDE.md                  # Hướng dẫn cho AI assistant
├── TECHNICAL_DOCS.md          # File này
│
├── controllers/
│   ├── main_window.py         # Màn hình đăng nhập
│   ├── overview_admin.py      # Dashboard Admin — lưới phòng + thống kê
│   ├── overview_users.py      # Trang chủ User — lưới phòng + đặt phòng + lịch sử
│   ├── booking_overview.py    # Admin — quản lý booking
│   ├── edit_room.py           # Admin — CRUD phòng
│   ├── users_management.py    # Admin — CRUD tài khoản
│   └── device_management.py   # Admin — quản lý thiết bị
│
├── models/
│   ├── user_model.py          # 6 hàm
│   ├── room_model.py          # 6 hàm
│   ├── booking_model.py       # 16 hàm
│   └── device_model.py        # 7 hàm
│
├── widgets/
│   ├── base_window.py         # Lớp cơ sở cho tất cả màn hình admin/user
│   ├── navbar.py              # Widget thanh điều hướng trên
│   ├── sidebar.py             # Widget sidebar trái (chỉ dành cho admin)
│   └── room_card.py           # Widget card phòng + trạng thái Full động
│
├── ui/                        # 18 file .ui của Qt Designer
│   ├── Login.ui
│   ├── MainWindow.ui
│   ├── navbar.ui
│   ├── sidebar.ui
│   ├── OverviewAdmin.ui
│   ├── OverviewUsers.ui
│   ├── BookingDialog.ui
│   ├── BookingHistory.ui
│   ├── BookingDetails.ui
│   ├── BookingManagement.ui
│   ├── AdminBookingDialog.ui
│   ├── RoomManagement.ui
│   ├── RoomDialog.ui
│   ├── Users.ui
│   ├── UserDialog.ui
│   ├── UserBookingsView.ui
│   ├── DeviceManagement.ui
│   └── DeviceDialog.ui
│
├── images/                    # 15 file ảnh (PNG + JPG)
│   ├── UEL_Logo.png
│   ├── background.jpg
│   ├── admin.png
│   ├── user.png
│   ├── eye_open.png
│   ├── eye_closed.png
│   ├── approve.png
│   ├── reject.png
│   ├── edit.png
│   ├── delete.png
│   ├── view.png
│   ├── search.png
│   ├── refresh.png
│   ├── reload.png
│   └── settings.png
│
└── datasets/
    └── smartlocker.db         # File cơ sở dữ liệu SQLite (tự động tạo)
```

### 1.5 Cài đặt & Chạy ứng dụng

```bash
# Cài đặt thư viện
pip install PyQt6

# Lần đầu chạy: reset DB và tạo dữ liệu mẫu
python3 seed.py

# Khởi động ứng dụng
python3 main.py
```

### 1.6 Tài khoản mặc định

Sau khi chạy `seed.py`, 10 tài khoản người dùng được tạo:

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | admin |
| `devadmin` | `devadmin` | admin |
| `devuser` | `devuser` | user |
| `sv001@st.uel.edu.vn` | `123456` | user |
| `sv002@st.uel.edu.vn` | `123456` | user |
| `sv003@st.uel.edu.vn` | `123456` | user |
| `sv004@st.uel.edu.vn` | `123456` | user |
| `sv005@st.uel.edu.vn` | `123456` | user |
| `gv001@uel.edu.vn` | `123456` | user |
| `gv002@uel.edu.vn` | `123456` | user |

---

## 2. Kiến trúc Hệ thống

### 2.1 Mô hình Kiến trúc

Ứng dụng theo mô hình **MVC đơn giản hóa** không dùng framework chính thức:

- **Model** — các hàm thuần túy trong `models/`, không có class, không có trạng thái. Mỗi hàm nhận tham số và trả về `dict` hoặc `list[dict]`.
- **View** — các file `.ui` thiết kế bằng Qt Designer, nạp vào lúc chạy qua `uic.loadUi()`.
- **Controller** — các class Python kế thừa `BaseWindow`, nạp file `.ui` vào `content_area` và kết nối signals/slots.

### 2.2 Luồng Điều hướng

```
main.py
  └── MainWindowController  (Login.ui)
        ├── [role = admin] ──> OverviewAdminController  (OverviewAdmin.ui)
        │                          ├── Sidebar: Overview   ──> (trang hiện tại)
        │                          ├── Sidebar: Bookings   ──> BookingOverviewController
        │                          ├── Sidebar: Edit       ──> EditRoomController
        │                          ├── Sidebar: Users      ──> UsersManagementController
        │                          ├── Sidebar: Devices    ──> DeviceManagementController
        │                          ├── Sidebar: Log Out    ──> MainWindowController
        │                          └── Sidebar: Quit       ──> QApplication.quit()
        │
        └── [role = user]  ──> OverviewUsersController  (OverviewUsers.ui)
                                   ├── Button: Booking     ──> BookingDialog  (QDialog)
                                   ├── Button: History     ──> BookingHistory (QDialog)
                                   │     ├── View          ──> BookingDetails (QDialog)
                                   │     ├── Edit          ──> BookingDialog  (QDialog, chế độ sửa)
                                   │     └── Cancel        ──> xóa booking Pending
                                   ├── Button: Log Out     ──> MainWindowController
                                   └── Button: Quit        ──> QApplication.quit()
```

**Mẫu chuyển màn hình:**
```python
new_controller = TargetController(self.current_user)
self._transfer_window_state(new_controller)   # giữ nguyên kích thước/vị trí/toàn màn hình
new_controller.show()
self.close()
```

### 2.3 Layout của BaseWindow

`BaseWindow` (`widgets/base_window.py`) là lớp cơ sở cho tất cả controller ngoại trừ `MainWindowController`. Nó tự động xây dựng layout sau:

```
QMainWindow
  └── centralWidget (QWidget)
        └── QVBoxLayout (margins=0, spacing=0)
              ├── NavBar  (QFrame — thanh trên với logo + tìm kiếm + nút vai trò)
              └── body    (QHBoxLayout, margins=0, spacing=0)
                    ├── SideBar  (QFrame — nav trái, tùy chọn)
                    └── QScrollArea (widgetResizable=True, không có khung)
                          └── content_area  (QWidget)
                                └── QVBoxLayout (margins=0)
                                      └── [UI được nạp bởi controller qua load_content_ui()]
```

Các controller gọi `self.load_content_ui("FileName.ui")` để nhúng màn hình của mình vào `content_area`. `QScrollArea` đảm bảo nội dung có thể cuộn khi cửa sổ quá nhỏ.

### 2.4 Bảng ánh xạ File UI — Controller (18 file)

| File .ui | Controller / Vị trí | Widget gốc | Mô tả |
|---|---|---|---|
| `Login.ui` | `controllers/main_window.py` | QMainWindow | Màn hình đăng nhập với ảnh nền |
| `MainWindow.ui` | `widgets/base_window.py` | — | (Không dùng trực tiếp, layout xây dựng bằng code) |
| `navbar.ui` | `widgets/navbar.py` | QFrame | Thanh điều hướng trên |
| `sidebar.ui` | `widgets/sidebar.py` | QFrame | Sidebar trái với 7 nút |
| `OverviewAdmin.ui` | `controllers/overview_admin.py` | QWidget | Dashboard Admin: thống kê + lưới phòng |
| `OverviewUsers.ui` | `controllers/overview_users.py` | QWidget | Trang chủ User: 3 nhóm filter + lưới phòng |
| `BookingDialog.ui` | inline trong `overview_users.py` | QDialog | Form tạo/sửa booking |
| `BookingHistory.ui` | inline trong `overview_users.py` | QDialog | Bảng lịch sử booking của user |
| `BookingDetails.ui` | inline trong `overview_users.py` + `booking_overview.py` | QDialog | Xem chi tiết booking (chỉ đọc) |
| `BookingManagement.ui` | `controllers/booking_overview.py` | QWidget | Bảng quản lý booking (Admin) |
| `AdminBookingDialog.ui` | inline trong `booking_overview.py` | QDialog | Form tạo/sửa/từ chối booking (Admin) |
| `RoomManagement.ui` | `controllers/edit_room.py` | QWidget | Bảng quản lý phòng (Admin) |
| `RoomDialog.ui` | inline trong `edit_room.py` | QDialog | Form thêm/sửa phòng |
| `Users.ui` | `controllers/users_management.py` | QWidget | Bảng quản lý tài khoản (Admin) |
| `UserDialog.ui` | inline trong `users_management.py` | QDialog | Form thêm/sửa tài khoản |
| `UserBookingsView.ui` | inline trong `users_management.py` | QDialog | Xem lịch sử booking của một user cụ thể |
| `DeviceManagement.ui` | `controllers/device_management.py` | QWidget | Bảng quản lý thiết bị (Admin) |
| `DeviceDialog.ui` | inline trong `device_management.py` | QDialog | Form thêm/sửa thiết bị |

---

## 3. Thiết kế Cơ sở dữ liệu

### 3.1 Sơ đồ Quan hệ Thực thể

```
┌──────────┐        ┌────────────┐        ┌──────────┐
│  users   │1      N│  bookings  │N      1│  rooms   │
│──────────│────────│────────────│────────│──────────│
│ id  (PK) │        │ id  (PK)   │        │ id  (PK) │
│ username │        │ user_id(FK)│        │ room_id  │
│ password │        │ room_id(FK)│        │ room_type│
│ role     │        │ date       │        │ capacity │
└──────────┘        │ time_start │        │ status   │
                    │ time_end   │        └──────┬───┘
                    │ reason     │               │ 1
                    │ status     │               │
                    │ reject_rsn │               │ N
                    │ locker_pw  │        ┌──────┴───┐
                    │ created_at │        │ devices  │
                    └────────────┘        │──────────│
                                          │ id  (PK) │
                                          │ room_id  │
                                          │ dev_name │
                                          │ cab_pw   │
                                          │ status   │
                                          └──────────┘
```

### 3.2 Bảng: `users`

```sql
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL,
    role     TEXT    NOT NULL CHECK(role IN ('admin', 'user'))
)
```

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Khóa chính |
| `username` | TEXT | UNIQUE, NOT NULL | Tên đăng nhập (định dạng email đối với sinh viên/giảng viên) |
| `password` | TEXT | NOT NULL | Chuỗi hex SHA-256 của mật khẩu gốc |
| `role` | TEXT | CHECK IN ('admin','user') | Cấp độ truy cập |

### 3.3 Bảng: `rooms`

```sql
CREATE TABLE IF NOT EXISTS rooms (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id   TEXT    UNIQUE NOT NULL,
    room_type TEXT    NOT NULL,
    capacity  INTEGER NOT NULL DEFAULT 50,
    status    TEXT    NOT NULL DEFAULT 'Available'
              CHECK(status IN ('Available', 'Occupied', 'Full'))
)
```

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Khóa chính |
| `room_id` | TEXT | UNIQUE, NOT NULL | Mã phòng dễ đọc (ví dụ: `A101`) |
| `room_type` | TEXT | NOT NULL | Loại phòng: Classroom, Lab, Meeting Room, Study Room |
| `capacity` | INTEGER | DEFAULT 50 | Số người tối đa |
| `status` | TEXT | CHECK, DEFAULT 'Available' | Trạng thái hiện tại của phòng |

> **Lưu ý:** Trạng thái `Full` được tính **động** tại runtime trong `widgets/room_card.py:get_display_status()`. Giá trị này không bao giờ được ghi vào database. Một phòng được coi là Full khi tất cả các slot 30 phút từ 06:00 đến 22:00 đều có ít nhất một booking đang hoạt động (Pending hoặc Approved) trong ngày hôm nay. Khi lọc theo "Available", các phòng bị Full động sẽ bị loại khỏi kết quả.

### 3.4 Bảng: `bookings`

```sql
CREATE TABLE IF NOT EXISTS bookings (
    id              INTEGER   PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER   NOT NULL,
    room_id         INTEGER   NOT NULL,
    date            TEXT      NOT NULL,
    time_start      TEXT      NOT NULL,
    time_end        TEXT      NOT NULL,
    reason          TEXT      NOT NULL,
    status          TEXT      NOT NULL DEFAULT 'Pending'
                    CHECK(status IN ('Pending', 'Approved', 'Rejected')),
    reject_reason   TEXT,
    locker_password TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
)
```

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Khóa chính |
| `user_id` | INTEGER | FK -> users(id) | Người đặt phòng |
| `room_id` | INTEGER | FK -> rooms(id) | Phòng được đặt |
| `date` | TEXT | NOT NULL | Ngày đặt phòng: `"YYYY-MM-DD"` |
| `time_start` | TEXT | NOT NULL | Giờ bắt đầu: `"HH:mm"` |
| `time_end` | TEXT | NOT NULL | Giờ kết thúc: `"HH:mm"` |
| `reason` | TEXT | NOT NULL | Mục đích sử dụng phòng |
| `status` | TEXT | CHECK, DEFAULT 'Pending' | Trạng thái duyệt |
| `reject_reason` | TEXT | NULL | Lý do từ chối (điền khi status = Rejected) |
| `locker_password` | TEXT | NULL | Mã 6 chữ số được sinh khi Approved |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Thời điểm tạo bản ghi |

### 3.5 Bảng: `devices`

```sql
CREATE TABLE IF NOT EXISTS devices (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id          INTEGER NOT NULL,
    device_name      TEXT    NOT NULL,
    cabinet_password TEXT,
    status           TEXT    NOT NULL DEFAULT 'Active'
                     CHECK(status IN ('Active', 'Inactive', 'Maintenance')),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
)
```

| Cột | Kiểu | Ràng buộc | Mô tả |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Khóa chính |
| `room_id` | INTEGER | FK -> rooms(id) | Phòng chứa thiết bị này |
| `device_name` | TEXT | NOT NULL | Nhãn thiết bị (ví dụ: `Smart Lock A101`) |
| `cabinet_password` | TEXT | NULL | Mã PIN tủ 6 chữ số |
| `status` | TEXT | CHECK, DEFAULT 'Active' | Trạng thái hoạt động |

---

## 4. Tầng Dữ liệu — Models

Tất cả file model chỉ chứa **các hàm thuần túy** — không có class, không có trạng thái chung. Mỗi hàm mở kết nối, thực thi truy vấn, đóng kết nối và trả về `dict` hoặc `list[dict]`. Ràng buộc khóa ngoại được bật qua `PRAGMA foreign_keys = ON` trong `database.py:get_connection()`.

### 4.1 `models/user_model.py` (6 hàm)

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `hash_password(password)` | `str` | `str` | Trả về chuỗi hex SHA-256 |
| `authenticate(username, password)` | `str, str` | `dict \| None` | Băm mật khẩu, SELECT WHERE khớp; trả về bản ghi user hoặc None |
| `get_all_users()` | — | `list[dict]` | Tất cả users (chỉ id, username, role) |
| `create_user(username, password, role)` | `str, str, str` | `bool` | Thêm user mới; trả về False nếu trùng username |
| `update_user(user_id, username, password, role)` | `int, str, str, str` | `bool` | Cập nhật user; mật khẩu rỗng = giữ nguyên hash hiện có |
| `delete_user(user_id)` | `int` | — | Xóa user theo id |

### 4.2 `models/room_model.py` (6 hàm)

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `get_all_rooms()` | — | `list[dict]` | Tất cả phòng (SELECT *) |
| `get_rooms_by_status(status)` | `str` | `list[dict]` | Lọc theo giá trị trạng thái |
| `search_rooms(keyword)` | `str` | `list[dict]` | Tìm kiếm LIKE trên room_id và room_type |
| `create_room(room_id, room_type, capacity, status)` | `str, str, int, str` | `bool` | Thêm phòng mới; mặc định status="Available" |
| `update_room(pk, room_id, room_type, capacity, status)` | `int, str, str, int, str` | `bool` | Cập nhật phòng theo khóa chính |
| `delete_room(pk)` | `int` | — | Xóa phòng theo khóa chính |

### 4.3 `models/booking_model.py` (16 hàm)

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `get_bookings_by_user(user_id)` | `int` | `list[dict]` | Tất cả booking của một user (JOIN rooms), ORDER BY created_at DESC |
| `get_all_bookings()` | — | `list[dict]` | Tất cả booking (JOIN rooms + users), ORDER BY created_at DESC |
| `create_booking(user_id, room_id, date, time_start, time_end, reason)` | `int, int, str, str, str, str` | `bool` | Tạo booking với status=Pending |
| `update_booking(booking_id, date, time_start, time_end, reason)` | `int, str, str, str, str` | — | Cập nhật thời gian/lý do (chỉ Pending) |
| `cancel_booking(booking_id)` | `int` | — | XÓA booking (chỉ Pending) |
| `_generate_locker_password()` | — | `str` | Nội bộ: chuỗi 6 chữ số ngẫu nhiên |
| `approve_booking(booking_id)` | `int` | `str` | Đặt Approved, sinh locker_password 6 chữ số, trả về mã đó |
| `reject_booking(booking_id, reason)` | `int, str` | — | Đặt Rejected, lưu reject_reason |
| `get_dashboard_stats()` | — | `dict` | Đếm: total_rooms, total_bookings, pending, approved, rejected |
| `delete_booking(booking_id)` | `int` | — | Xóa cứng (Admin, mọi trạng thái) |
| `admin_update_booking(booking_id, date, time_start, time_end, reason, status)` | `int, str, str, str, str, str` | — | Cập nhật đầy đủ của Admin (ngày + giờ + lý do + trạng thái) |
| `get_all_users_simple()` | — | `list[dict]` | SELECT id, username ORDER BY username |
| `get_bookings_by_room(room_pk)` | `int` | `list[dict]` | Booking đang hoạt động (Pending/Approved) của một phòng — trả về date, time_start, time_end, status |
| `get_bookings_by_room_date(room_pk, date_str)` | `int, str` | `list[dict]` | Booking đang hoạt động của một phòng trong một ngày cụ thể (WHERE date = ?) |
| `_to_minutes(t)` | `str` | `int` | Chuyển "HH:mm" thành số phút từ nửa đêm |
| `has_conflict(room_pk, date_str, start_str, end_str, exclude_id)` | `int, str, str, str, int\|None` | `bool` | Kiểm tra trùng lịch; exclude_id bỏ qua một booking (dùng khi sửa) |

**Thuật toán phát hiện xung đột:**

Hai khoảng thời gian `[ns, ne)` và `[bs, be)` giao nhau khi:
```
ns < be  VÀ  ne > bs
```
Đây là phép kiểm tra giao khoảng chuẩn. Hàm chuyển chuỗi `"HH:mm"` thành số phút từ nửa đêm qua `_to_minutes()` trước khi so sánh.

### 4.4 `models/device_model.py` (7 hàm)

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `get_all_devices()` | — | `list[dict]` | Tất cả thiết bị (JOIN rooms lấy room_id làm room_name), ORDER BY room_id, device_name |
| `search_devices(keyword)` | `str` | `list[dict]` | Tìm kiếm LIKE trên room_id, device_name, status |
| `create_device(room_id, device_name, status)` | `int, str, str` | `bool` | Thêm thiết bị mới; mặc định status="Active" |
| `update_device_password(device_id, new_password)` | `int, str` | — | Cập nhật cabinet_password |
| `update_device_status(device_id, status)` | `int, str` | — | Cập nhật trạng thái thiết bị |
| `delete_device(device_id)` | `int` | — | Xóa thiết bị |
| `generate_password()` | — | `str` | Trả về chuỗi 6 chữ số ngẫu nhiên |

---

## 5. Controllers

### 5.1 `MainWindowController` (`controllers/main_window.py`)

Kế thừa trực tiếp `QMainWindow` (không phải `BaseWindow`). Nạp `Login.ui`.

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__()` | Nạp Login.ui, init_db(), thiết lập nền/UI/signals, kích thước tối thiểu 1000x600 |
| `_setup_background()` | Class động `BgCentral` với mixin `_BgWidget`, vẽ `background.jpg` scale-to-cover |
| `_make_login_responsive()` | Card đăng nhập nền trắng `rgba(255,255,255,0.92)`, border-radius 12px |
| `_setup_ui()` | Đặt pixmap logo, icon mắt để ẩn/hiện mật khẩu, định dạng màu chữ input |
| `_connect_signals()` | pushButtonLogin, btnTogglePassword, returnPressed trên cả hai input |
| `_toggle_password()` | Chuyển đổi EchoMode Normal/Password, đổi icon eye_open/eye_closed |
| `_handle_login()` | Xác thực input -> authenticate() -> kiểm tra vai trò khớp radio button -> _open_dashboard() |
| `_toggle_fullscreen()` | Xử lý phím tắt F11 |
| `_open_dashboard(user)` | role='admin' -> OverviewAdminController, role='user' -> OverviewUsersController |

**Luồng đăng nhập:**
1. Người dùng nhập username + password, chọn radio button vai trò (Admin / User)
2. `authenticate(username, password)` băm input bằng SHA-256 và so sánh với DB
3. Nếu thông tin đúng nhưng vai trò không khớp radio button -> thông báo lỗi
4. Thành công -> khởi tạo controller phù hợp, hiển thị, đóng màn hình đăng nhập

**Mixin `_BgWidget`:** Ghi đè `paintEvent` để vẽ `background.jpg` với `KeepAspectRatioByExpanding` + `SmoothTransformation`, căn giữa trên widget.

### 5.2 `OverviewAdminController` (`controllers/overview_admin.py`)

Kế thừa `BaseWindow`. Nạp `OverviewAdmin.ui`. Tham số: `show_search=True, show_sidebar=True`.

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__(user)` | Nạp UI, kết nối signals, tải thống kê + phòng |
| `_connect_sidebar()` | Override: pushButtonOverview -> lambda: None (trang hiện tại) |
| `_connect_signals()` | Nút filter (All/Available/Occupied/Full) + tìm kiếm navbar |
| `_load_rooms()` | Kết hợp tìm kiếm keyword + filter trạng thái + loại Full khỏi Available |
| `_render_room_cards(rooms)` | Lưu `_rooms_data`, gọi `_reflow_grid()` |
| `_reflow_grid()` | Tính số cột, xóa layout, thêm card theo dạng lưới |
| `showEvent(event)` / `resizeEvent(event)` | Gọi `_reflow_grid()` cho layout responsive |
| `_create_room_card(room)` | Ủy quyền cho `create_room_card(room, on_context=...)` |
| `_on_card_context(room, global_pos)` | Menu ngữ cảnh: "Edit Room" -> `_go_edit(preselect_room=room)` |
| `_apply_filter(status)` | Đặt `_current_filter`, tải lại phòng |
| `_on_search()` | Tải lại phòng với keyword hiện tại |
| `_load_stats()` | `get_dashboard_stats()` -> đặt 5 nhãn thống kê |

**Thống kê Dashboard hiển thị:** Tổng phòng, Tổng booking, Pending, Approved, Rejected.

**Logic filter Available:** Khi filter là "Available", các phòng có `get_display_status(room) == "Full"` bị loại khỏi kết quả. Điều này đảm bảo các phòng Full động không hiển thị là available.

### 5.3 `OverviewUsersController` (`controllers/overview_users.py`)

Kế thừa `BaseWindow`. Nạp `OverviewUsers.ui`. Tham số: `show_search=True, show_sidebar=False`.

**Ba nhóm filter độc lập:**

| Nhóm | Tùy chọn | Biến trạng thái |
|---|---|---|
| Trạng thái | All / Available / Occupied / Full | `_current_filter` |
| Sức chứa | All / <=50 / 100+ | `_capacity_filter` |
| Ca học | All / Morning (06-12) / Afternoon (12-17) / Evening (17-22) | `_time_filter` |

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__(user)` | Khởi tạo 3 trạng thái filter thành "All", nạp UI, kết nối signals, tải phòng |
| `_connect_signals()` | 12 nút filter + tìm kiếm navbar + nút History/Booking/Logout/Quit |
| `_apply_filter(status)` / `_apply_capacity(cap)` / `_apply_time(session)` | Đặt trạng thái filter, tải lại phòng |
| `_load_rooms()` | Chuỗi: keyword/status -> loại Full khỏi Available -> sức chứa -> filter ca học |
| `_has_free_slot(room_pk, date_str, range_start, range_end)` | Tĩnh: kiểm tra xem có slot 30 phút nào còn trống trong khoảng |
| `_render_room_cards(rooms)` / `_reflow_grid()` | Cùng mẫu lưới responsive như Admin |
| `_on_card_context(room, global_pos)` | Menu ngữ cảnh: "Book Room" -> `_open_booking_dialog(room)` |
| `_open_booking_dialog(preselect_room)` | Nạp BookingDialog.ui, điền combos, xác thực, create_booking() |
| `_refresh_availability(dlg)` | Xây bảng availability 16 cột (06-21h), tô màu theo trạng thái |
| `_show_history()` | Nạp BookingHistory.ui, comboFilter, điền bảng |
| `_populate_history(dlg, filter_text)` | Điền bảng 10 cột với nút hành động mỗi hàng |
| `_view_booking(booking_id, parent_dlg)` | Nạp BookingDetails.ui, ẩn trường User |
| `_edit_booking(booking_id, history_dlg)` | Nạp BookingDialog.ui ở chế độ sửa, vô hiệu hóa comboRoom |
| `_cancel_booking(booking_id, dlg)` | Xác nhận -> cancel_booking() -> làm mới |

**Hằng số khoảng thời gian:**
```python
TIME_RANGES = {
    "Morning":   (360, 720),    # 06:00 - 12:00
    "Afternoon": (720, 1020),   # 12:00 - 17:00
    "Evening":   (1020, 1320),  # 17:00 - 22:00
}
```

**Tính năng Booking Dialog:**
- Combo phòng chỉ hiển thị phòng Available
- Date picker: ngày tối thiểu là hôm nay
- Time edit: bắt đầu 06:00-21:59, kết thúc 06:01-22:00
- Bảng availability: 16 cột (giờ 06-21), tô màu theo trạng thái:
  - Xanh lá (`#A5D6A7`) = trống
  - Vàng (`#FFE082`) = booking Pending
  - Đỏ (`#EF9A9A`) = booking Approved
- Xác thực: phải có mục đích, giờ kết thúc > bắt đầu, giờ trong 06:00-22:00, không trùng lịch

**Tính năng Booking History:**
- Lọc theo trạng thái (All Status / Pending / Approved / Rejected)
- 10 cột: Room, Type, Date, Start, End, Reason, Status (có màu), Locker Password, Reject Reason (đỏ), Actions
- Cột Actions (cố định 100px): View (luôn hiện) + Edit + Cancel (chỉ khi Pending)
- Nút hành động dùng icon PNG: `view.png`, `edit.png`, `delete.png`

### 5.4 `BookingOverviewController` (`controllers/booking_overview.py`)

Kế thừa `BaseWindow`. Nạp `BookingManagement.ui`. Tham số: `show_search=False, show_sidebar=True`.

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__(user)` | Nạp UI, kết nối signals, tải bảng |
| `_connect_sidebar()` | pushButtonBookings -> lambda: None (trang hiện tại) |
| `_connect_signals()` | Nút filter + lineEditSearch + nút Add/Import/Export |
| `_load_table()` | get_all_bookings() -> lọc trạng thái + keyword -> điền bảng |
| `_make_icon_btn(icon_file, tooltip, bg, hover, slot)` | Helper: tạo nút icon 22x22 có style |
| `_make_actions_widget(booking_id, status)` | View (luôn hiện) + Approve/Reject (Pending) + Edit + Delete |
| `_view_booking(booking_id)` | Nạp BookingDetails.ui, hiển thị trường User |
| `_approve_booking_inline(booking_id)` | approve_booking() -> hiển thị mật khẩu trong QMessageBox |
| `_reject_booking_inline(booking_id)` | _build_booking_dialog(reject_mode=True) -> reject_booking() |
| `_add_booking()` | _build_booking_dialog() -> create_booking() |
| `_edit_booking(booking_id)` | _build_booking_dialog(booking) -> admin_update_booking() |
| `_delete_booking(booking_id)` | Xác nhận -> delete_booking() |
| `_import_csv()` | Cột CSV: username, room_id, date, start_time, end_time, reason |
| `_export_csv()` | Xuất view đã lọc: User, Room, Type, Date, Start Time, End Time, Purpose, Status, Locker Password |
| `_build_booking_dialog(booking, reject_mode)` | Nạp AdminBookingDialog.ui, điền combos |

**Cột bảng (10):** User, Room, Type, Date, Start, End, Purpose, Status (có màu), Locker Password, Actions (cố định 130px).

**Các chế độ AdminBookingDialog:**
- **Chế độ thêm:** Ẩn labelStatus, comboStatus, labelRejectReason, editRejectReason
- **Chế độ sửa:** Hiển thị tất cả trường ngoại trừ reject reason
- **Chế độ từ chối:** Vô hiệu hóa tất cả trường ngoại trừ editRejectReason; ẩn combo trạng thái

### 5.5 `EditRoomController` (`controllers/edit_room.py`)

Kế thừa `BaseWindow`. Nạp `RoomManagement.ui`. Tham số: `show_search=False, show_sidebar=True`.

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__(user, preselect_room=None)` | Nạp UI, kết nối signals, tải bảng, chọn sẵn nếu có |
| `_connect_sidebar()` | pushButtonEdit -> lambda: None (trang hiện tại) |
| `_connect_signals()` | Filter (All/Available/Occupied) + lineEditSearch + Add + nút CSV |
| `_apply_filter()` | Lọc theo radio trạng thái + keyword (room_id, room_type) |
| `_populate_table(rooms)` | 5 cột: room_id, room_type, capacity, status (có màu), actions (cố định 72px) |
| `_make_actions_widget(room)` | Nút Edit + Delete (22x22 với icon PNG) |
| `_preselect(room)` | Chọn hàng khớp room_id trong bảng |
| `_build_room_dialog(room)` | Nạp RoomDialog.ui, điền sẵn nếu đang sửa |
| `_add_room()` | Xác thực room_id, room_type, capacity (int) -> create_room() |
| `_edit_room(room)` | Xác thực -> update_room() |
| `_delete_room(room_pk)` | Xác nhận -> delete_room() |
| `_import_csv()` | Cột CSV: room_id, room_type, capacity, status |
| `_export_csv()` | Xuất: room_id, room_type, capacity, status |

**Màu trạng thái trong bảng:** Available=#4CAF50, Occupied=#FF9800, Cleaning=#2196F3, Full=#F44336.

### 5.6 `UsersManagementController` (`controllers/users_management.py`)

Kế thừa `BaseWindow`. Nạp `Users.ui`. Tham số: `show_search=False, show_sidebar=True`.

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__(user)` | Nạp UI, kết nối signals, tải bảng |
| `_connect_sidebar()` | pushButtonUsers -> lambda: None (trang hiện tại) |
| `_connect_signals()` | Filter (All/Admin/User) + lineEditSearch + Add + nút CSV |
| `_apply_filter()` | Lọc theo radio vai trò + keyword (username) |
| `_populate_table(users)` | 3 cột: username, role (có màu), actions (cố định 100px) |
| `_make_actions_widget(user)` | Nút View Bookings (tím) + Edit (xanh) + Delete (đỏ) |
| `_build_user_dialog(user)` | Nạp UserDialog.ui, điền sẵn nếu đang sửa |
| `_add_user()` | Xác thực username + password -> create_user() |
| `_edit_user(user)` | Xác thực username -> update_user() (mật khẩu là tùy chọn) |
| `_delete_user(user_id)` | Bảo vệ: không thể xóa chính mình -> Xác nhận -> delete_user() |
| `_view_user_bookings(user)` | Nạp UserBookingsView.ui, bảng 7 cột |
| `_import_csv()` | Cột CSV: username, password, role |
| `_export_csv()` | Xuất: username, role (không có mật khẩu) |

**Màu vai trò:** admin=#E91E63 (hồng), user=#4CAF50 (xanh lá).

**Bảng UserBookingsView (7 cột):** Room, Type, Date, Start, End, Reason, Status (có màu).

### 5.7 `DeviceManagementController` (`controllers/device_management.py`)

Kế thừa `BaseWindow`. Nạp `DeviceManagement.ui`. Tham số: `show_search=False, show_sidebar=True`.

**Các phương thức chính:**

| Phương thức | Mô tả |
|---|---|
| `__init__(user)` | Nạp UI, kết nối signals, tải bảng |
| `_connect_sidebar()` | pushButtonDevices -> lambda: None (trang hiện tại) |
| `_connect_signals()` | Filter (All/Active/Inactive/Maintenance) + lineEditSearch + Add + nút CSV |
| `_apply_filter()` | Lọc theo radio trạng thái + keyword (room_name, device_name) |
| `_populate_table(devices)` | 5 cột: room, device_name, cabinet_password, status (có màu), actions (cố định 100px) |
| `_make_actions_widget(device)` | Nút Edit + Delete |
| `_build_device_dialog(device)` | Nạp DeviceDialog.ui, điền comboRoom |
| `_add_device()` | Xác thực device_name -> create_device() |
| `_edit_device(device)` | update_device_status() luôn chạy + update_device_password() nếu có mật khẩu mới |
| `_delete_device(device_id)` | Xác nhận -> delete_device() |
| `_import_csv()` | Cột CSV: room_id, device_name, status |
| `_export_csv()` | Xuất: room, device_name, cabinet_password, status |

**Các chế độ DeviceDialog:**
- **Chế độ thêm:** Ẩn labelPw + pwWidget (không có trường mật khẩu)
- **Chế độ sửa:** Hiển thị editPw + btnGenPw (icon refresh.png), nhấn để sinh mật khẩu 6 chữ số ngẫu nhiên

**Màu trạng thái:** Active=#4CAF50, Inactive=#9E9E9E, Maintenance=#FF9800.

---

## 6. Widgets

### 6.1 `BaseWindow` (`widgets/base_window.py`)

Lớp cơ sở cho tất cả controller ngoại trừ `MainWindowController`. Kích thước tối thiểu 800x500, mặc định 1200x800.

| Phương thức | Tham số | Mô tả |
|---|---|---|
| `__init__` | `user, role_text="Admin", show_search=False, show_sidebar=True, title="SmartLocker UEL"` | Xây dựng layout NavBar + SideBar tùy chọn + ScrollArea |
| `_connect_sidebar()` | — | Kết nối 7 nút sidebar với các phương thức điều hướng. Override trong subclass để đặt trang hiện tại thành `lambda: None` |
| `load_content_ui(filename)` | `str` | Nạp `ui/<filename>` vào `content_area` qua `uic.loadUi()`, trả về widget |
| `_go_overview()` | — | Điều hướng tới `OverviewAdminController` |
| `_go_bookings()` | — | Điều hướng tới `BookingOverviewController` |
| `_go_edit(preselect_room=None)` | `dict\|None` | Điều hướng tới `EditRoomController` |
| `_go_users()` | — | Điều hướng tới `UsersManagementController` |
| `_go_devices()` | — | Điều hướng tới `DeviceManagementController` |
| `_transfer_window_state(target)` | `QMainWindow` | Sao chép trạng thái toàn màn hình/phóng to/kích thước+vị trí sang cửa sổ đích |
| `_toggle_fullscreen()` | — | Xử lý F11: chuyển đổi toàn màn hình/thường |
| `_logout()` | — | Hộp thoại xác nhận -> quay về `MainWindowController` |
| `_quit()` | — | Tĩnh. Hộp thoại xác nhận -> `QApplication.quit()` |

### 6.2 `NavBar` (`widgets/navbar.py`)

Nạp từ `navbar.ui`. Widget `QFrame` chứa thanh điều hướng trên.

| Phần tử | Mô tả |
|---|---|
| `btnRole` | Hiển thị văn bản vai trò ("Admin" hoặc "User") với icon theo vai trò |
| `lineEditSearch` | Input tìm kiếm thời gian thực, ẩn khi `show_search=False` |

**Logic icon:**
- `role_text == "Admin"` -> icon `admin.png`
- role_text khác -> icon `user.png`
- Kích thước icon: 20x20

### 6.3 `SideBar` (`widgets/sidebar.py`)

Nạp từ `sidebar.ui`. Widget `QFrame` chứa các nút điều hướng cho màn hình admin.

**Các nút (7):**
- `pushButtonOverview` — Dashboard
- `pushButtonBookings` — Quản lý Booking
- `pushButtonEdit` — Quản lý Phòng
- `pushButtonUsers` — Quản lý Tài khoản
- `pushButtonDevices` — Quản lý Thiết bị
- `pushButtonLogOut` — Đăng xuất
- `pushButtonQuit` — Thoát ứng dụng

Mỗi controller override `_connect_sidebar()` để đặt nút của chính mình thành `lambda: None` (no-op cho trang hiện tại) trong khi kết nối các nút còn lại với các phương thức điều hướng.

### 6.4 `room_card` (`widgets/room_card.py`)

Các hàm cấp module để tạo widget card phòng và tính trạng thái động.

**Hằng số:**
```python
OP_START = 6 * 60   # 360 phút (06:00)
OP_END   = 22 * 60  # 1320 phút (22:00)

STATUS_COLORS = {"Available": "#4CAF50", "Occupied": "#F44336", "Full": "#FF9800"}
STATUS_BG     = {"Available": "#E8F5E9", "Occupied": "#FFEBEE", "Full": "#FFF3E0"}
```

**Các hàm:**

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `_to_minutes(t)` | `str` | `int` | Chuyển "HH:mm" thành số phút từ nửa đêm |
| `_is_full_today(room_pk)` | `int` | `bool` | Kiểm tra tất cả slot 30 phút (06:00-22:00) đã được đặt hôm nay chưa |
| `get_display_status(room)` | `dict` | `str` | Nếu status=="Available" và _is_full_today() -> "Full", ngược lại room["status"] |
| `create_room_card(room, on_context)` | `dict, callable\|None` | `QWidget` | Tạo card 200x110 với viền, tiêu đề, loại/sức chứa, số lượng booking |

**Layout card:**
```
QWidget (200x110, border 2px solid {status_color}, border-radius 10px)
  └── QVBoxLayout (margins 12,10,12,10, spacing 6)
        ├── QHBoxLayout (tiêu đề)
        │     ├── QLabel room_id (đậm, 14px)
        │     ├── stretch
        │     └── QLabel badge trạng thái (có màu, bo góc, 10px)
        ├── QLabel "{room_type}  ·  {capacity} chỗ" (xám, 11px)
        ├── QFrame HLine (đường kẻ ngang, #F0F0F0)
        └── QLabel "{N} booking đang hoạt động" hoặc "Không có booking" (căn giữa)
```

**Menu ngữ cảnh:** Khi `on_context` được cung cấp, click chuột phải kích hoạt `on_context(room, global_pos)`.

---

## 7. Thuật toán và Logic Nghiệp vụ Chính

### 7.1 Phát hiện Xung đột Booking

`models/booking_model.py:has_conflict()`

```python
def has_conflict(room_pk, date_str, start_str, end_str, exclude_id=None):
    bookings = get_bookings_by_room_date(room_pk, date_str)
    ns, ne = _to_minutes(start_str), _to_minutes(end_str)
    for b in bookings:
        if exclude_id is not None and b["id"] == exclude_id:
            continue
        bs, be = _to_minutes(b["time_start"]), _to_minutes(b["time_end"])
        if ns < be and ne > bs:   # kiểm tra giao khoảng chuẩn
            return True
    return False
```

Tham số `exclude_id` cho phép sửa booking hiện có mà không bị xung đột với chính nó.

### 7.2 Trạng thái "Full" Động

`widgets/room_card.py:_is_full_today()`

```python
def _is_full_today(room_pk):
    today = date.today().strftime("%Y-%m-%d")
    bookings = get_bookings_by_room_date(room_pk, today)
    booked = set()
    for b in bookings:
        start = max(_to_minutes(b["time_start"]), OP_START)
        end   = min(_to_minutes(b["time_end"]), OP_END)
        for slot in range(start, end, 30):
            booked.add(slot)
    all_slots = set(range(OP_START, OP_END, 30))  # 06:00-22:00, 32 slots
    return all_slots.issubset(booked)
```

### 7.3 Filter Available Loại trừ Full

Cả `OverviewAdminController` và `OverviewUsersController` đều áp dụng logic này:

```python
if self._current_filter == "Available":
    rooms = [r for r in rooms if get_display_status(r) != "Full"]
```

Điều này đảm bảo các phòng về mặt kỹ thuật là "Available" trong database nhưng bị Full động (tất cả slot đã đặt hôm nay) sẽ bị loại khi người dùng lọc theo "Available".

### 7.4 Layout Lưới Responsive

Dùng trong cả controller Admin và User:

```python
card_w  = 200
spacing = layout.horizontalSpacing() or 10
available = self.content_area.width() - 20
cols = max(1, available // (card_w + spacing))
```

Được tính lại trong cả `resizeEvent` và `showEvent` để thích ứng với mọi kích thước cửa sổ. Các card được đặt trong `QGridLayout` tại vị trí `(i // cols, i % cols)`. Stretch được thêm sau hàng và cột cuối cùng để đẩy card về góc trên-trái.

### 7.5 Sinh Mật khẩu Tủ khóa

`models/booking_model.py:_generate_locker_password()`

```python
def _generate_locker_password():
    return "".join(random.choices(string.digits, k=6))
```

Được gọi tự động khi admin duyệt booking qua `approve_booking()`. Mã 6 chữ số được lưu vào `bookings.locker_password` và hiển thị ngay cho admin, cũng như cho user trong Booking History.

### 7.6 Filter Theo Ca học (`_has_free_slot`)

`controllers/overview_users.py:_has_free_slot()` (staticmethod)

```python
TIME_RANGES = {
    "Morning":   (360, 720),    # 06:00 - 12:00
    "Afternoon": (720, 1020),   # 12:00 - 17:00
    "Evening":   (1020, 1320),  # 17:00 - 22:00
}

@staticmethod
def _has_free_slot(room_pk, date_str, range_start, range_end):
    bookings = get_bookings_by_room_date(room_pk, date_str)
    booked = set()
    for b in bookings:
        # thêm các slot 30 phút vào tập booked
        for slot in range(start_min, end_min, 30):
            booked.add(slot)
    return any(slot not in booked for slot in range(range_start, range_end, 30))
```

Một phòng vượt qua filter ca học nếu có **ít nhất một slot 30 phút còn trống** trong khoảng thời gian được chọn hôm nay.

### 7.7 Render Bảng Availability

`controllers/overview_users.py:_refresh_availability()`

`BookingDialog` hiển thị bảng 16 cột (mỗi cột một giờ, 06-21). Với mỗi slot giờ:

```
slot_s = hour * 60
slot_e = (hour + 1) * 60

Với mỗi booking đang hoạt động [bs, be, status]:
    if bs < slot_e and be > slot_s:   -> slot bị chiếm
        if status == "Approved" -> ĐỎ   (#EF9A9A)
        elif status == "Pending" -> VÀNG (#FFE082)
    else                        -> XANH (#A5D6A7)
```

Ưu tiên: Approved (đỏ) được ưu tiên hơn Pending (vàng) nếu cả hai cùng giao với một giờ.

---

## 8. Tài nguyên

### 8.1 File Hình ảnh (15 file trong `images/`)

| File | Cách dùng |
|---|---|
| `UEL_Logo.png` | Logo màn hình đăng nhập (scale về 120x120) |
| `background.jpg` | Ảnh nền màn hình đăng nhập (scale-to-cover qua paintEvent) |
| `admin.png` | Icon vai trò NavBar cho người dùng Admin |
| `user.png` | Icon vai trò NavBar cho người dùng không phải Admin |
| `eye_open.png` | Nút ẩn/hiện mật khẩu đăng nhập — trạng thái hiển thị |
| `eye_closed.png` | Nút ẩn/hiện mật khẩu đăng nhập — trạng thái ẩn |
| `approve.png` | Nút hành động bảng booking — duyệt booking |
| `reject.png` | Nút hành động bảng booking — từ chối booking |
| `edit.png` | Nút hành động bảng — sửa bản ghi (phòng, tài khoản, thiết bị, booking, lịch sử) |
| `delete.png` | Nút hành động bảng — xóa/hủy bản ghi |
| `view.png` | Nút hành động bảng — xem chi tiết (bookings, lịch sử user) |
| `search.png` | Icon tìm kiếm trong thanh tìm kiếm của UI quản lý (dùng như pixmap trong file .ui) |
| `refresh.png` | Dialog thiết bị — icon nút sinh mật khẩu mới |
| `reload.png` | Icon reload/làm mới chung |
| `settings.png` | Icon cài đặt |

**Mẫu nút icon:** Tất cả nút hành động trong bảng là `QPushButton` 22x22 với kích thước icon 14x14, được style với nền có màu + hiệu ứng hover, border-radius 5-6px, không có viền.

---

## 9. Dữ liệu Mẫu

Chạy `python3 seed.py` sẽ xóa database hiện có và tạo lại với dữ liệu sau:

### 9.1 Tài khoản (10 tổng)

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | admin |
| `devadmin` | `devadmin` | admin |
| `devuser` | `devuser` | user |
| `sv001@st.uel.edu.vn` | `123456` | user |
| `sv002@st.uel.edu.vn` | `123456` | user |
| `sv003@st.uel.edu.vn` | `123456` | user |
| `sv004@st.uel.edu.vn` | `123456` | user |
| `sv005@st.uel.edu.vn` | `123456` | user |
| `gv001@uel.edu.vn` | `123456` | user |
| `gv002@uel.edu.vn` | `123456` | user |

### 9.2 Phòng (12 tổng)

| Mã phòng | Loại | Sức chứa | Trạng thái |
|---|---|---|---|
| A101 | Classroom | 50 | Available |
| A102 | Classroom | 50 | Available |
| A201 | Classroom | 100 | Available |
| B101 | Meeting Room | 20 | Available |
| B102 | Meeting Room | 20 | Occupied |
| C101 | Study Room | 10 | Available |
| C102 | Study Room | 10 | Available |
| C103 | Study Room | 10 | Available |
| D101 | Lab | 40 | Available |
| D102 | Lab | 40 | Available |
| E101 | Classroom | 50 | Available |
| E102 | Classroom | 50 | Available |

### 9.3 Thiết bị (12 tổng)

Mỗi phòng có một thiết bị Smart Lock. Tất cả thiết bị đều có mật khẩu 6 chữ số được sinh tự động, ngoại trừ:
- **Smart Lock C103**: `cabinet_password = NULL`, trạng thái = `Maintenance`
- **Smart Lock B102**: trạng thái = `Inactive`

### 9.4 Booking (10 tổng)

| Người dùng | Phòng | Ngày | Giờ | Trạng thái | Ghi chú |
|---|---|---|---|---|---|
| sv001@st.uel.edu.vn | A101 | 2026-03-10 | 07:00-09:30 | Approved | Có locker_password |
| sv002@st.uel.edu.vn | A101 | 2026-03-10 | 09:45-12:15 | Approved | Có locker_password |
| sv003@st.uel.edu.vn | B101 | 2026-03-10 | 12:30-15:00 | Pending | |
| sv004@st.uel.edu.vn | C101 | 2026-03-10 | 15:15-17:45 | Pending | |
| sv005@st.uel.edu.vn | A102 | 2026-03-11 | 07:00-09:30 | Rejected | Lý do: "Room reserved for faculty use" |
| gv001@uel.edu.vn | B101 | 2026-03-11 | 09:45-12:15 | Approved | Có locker_password |
| sv001@st.uel.edu.vn | D101 | 2026-03-11 | 12:30-15:00 | Pending | |
| sv002@st.uel.edu.vn | E101 | 2026-03-12 | 07:00-09:30 | Approved | Có locker_password |
| sv003@st.uel.edu.vn | C102 | 2026-03-12 | 09:45-12:15 | Pending | |
| gv002@uel.edu.vn | A201 | 2026-03-12 | 15:15-17:45 | Rejected | Lý do: "Overlapping with scheduled class" |
