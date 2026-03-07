# Tài liệu kỹ thuật — SmartLocker UEL

**Phiên bản:** 1.0
**Ngày cập nhật:** 2026-03-07
**Nền tảng:** Python 3.10+, PyQt6, SQLite

---

## 1. Tổng quan hệ thống

SmartLocker UEL là ứng dụng desktop quản lý đặt phòng/tủ thiết bị cho Trường Đại học Kinh tế - Luật (UEL). Hệ thống hỗ trợ hai vai trò người dùng:

- **Admin**: quản lý phòng, người dùng, duyệt/từ chối booking
- **User (Giảng viên/Sinh viên)**: xem phòng, đặt phòng, xem lịch sử booking

---

## 2. Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|---|---|
| Python | 3.10 trở lên |
| PyQt6 | `pip install PyQt6` |
| Hệ điều hành | Windows / macOS / Linux |
| Cơ sở dữ liệu | SQLite (tích hợp sẵn, không cần cài thêm) |

---

## 3. Cài đặt và khởi chạy

```bash
# Cài thư viện
pip install PyQt6

# Lần đầu: khởi tạo DB và seed dữ liệu mẫu
python3 seed.py

# Khởi động ứng dụng
python3 main.py
```

Tài khoản mặc định sau khi seed:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | admin |
| `sv001@st.uel.edu.vn` | `123456` | user |

---

## 4. Cấu trúc thư mục

```
SmartLockUEL/
├── main.py                     # Entry point
├── database.py                 # Kết nối SQLite, khởi tạo schema
├── seed.py                     # Seed dữ liệu mẫu
├── TECHNICAL_DOCS.md           # Tài liệu kỹ thuật (file này)
│
├── models/                     # Tầng dữ liệu (pure functions)
│   ├── user_model.py
│   ├── room_model.py
│   └── booking_model.py
│
├── widgets/                    # Widget dùng chung
│   ├── base_window.py          # BaseWindow — lớp cha của mọi controller
│   ├── navbar.py               # NavBar widget
│   ├── sidebar.py              # SideBar widget
│   └── room_card.py            # Room card widget + SESSIONS constant
│
├── controllers/                # Điều khiển từng màn hình
│   ├── main_window.py          # Màn hình Login
│   ├── overview_admin.py       # Dashboard Admin
│   ├── overview_users.py       # Dashboard User
│   ├── edit_room.py            # Room Management (CRUD phòng)
│   ├── booking_overview.py     # Booking Overview (CRUD booking)
│   └── users_management.py     # Users Management (CRUD user)
│
├── ui/                         # File giao diện Qt Designer (.ui)
│   ├── Login.ui
│   ├── navbar.ui
│   ├── sidebar.ui
│   ├── OverviewAdmin.ui
│   ├── OverviewUsers.ui
│   ├── BookingDialog.ui
│   ├── BookingApproval.ui
│   ├── BookingHistory.ui
│   ├── BookingOverview.ui
│   ├── RoomManagement.ui
│   └── Users.ui
│
├── images/                     # Tài nguyên hình ảnh
│   ├── background.jpg
│   ├── UEL_Logo final-09.png
│   ├── admin.png
│   ├── users.png
│   ├── eye_open.png
│   └── eye_closed.png
│
└── datasets/
    └── smartlocker.db          # File SQLite (tự tạo khi chạy seed.py)
```

---

## 5. Kiến trúc phần mềm

### 5.1 Mô hình tổng thể

Ứng dụng không theo MVC chuẩn mà dùng mô hình **Controller-Widget** đơn giản:

```
main.py
  └── MainWindowController (Login)
        ├── OverviewAdminController  ←→  EditRoomController
        │         ↕ sidebar               BookingOverviewController
        │                                 UsersManagementController
        └── OverviewUsersController
```

Mọi controller kế thừa `BaseWindow`, load file `.ui` vào `content_area`, và override `_connect_sidebar()` nếu cần.

### 5.2 Luồng điều hướng

```
Login
  │
  ├─[role=admin]─→ OverviewAdminController
  │                    ├─[sidebar: Room Overview]─→ OverviewAdminController
  │                    ├─[sidebar: Booking Overview]─→ BookingOverviewController
  │                    ├─[sidebar: Room Management]─→ EditRoomController
  │                    ├─[sidebar: Users]─→ UsersManagementController
  │                    └─[sidebar: Log out]─→ Login
  │
  └─[role=user]──→ OverviewUsersController
                       ├─[btnBooking]─→ BookingDialog (QDialog)
                       ├─[navbar btnRole]─→ BookingHistory (QDialog)
                       └─[btnLogout]─→ Login
```

Khi navigate giữa các tab, `_transfer_window_state()` trong `BaseWindow` giữ nguyên kích thước/trạng thái cửa sổ (fullscreen, maximized, hoặc kích thước thường).

### 5.3 BaseWindow

`widgets/base_window.py` — lớp cha của mọi controller admin.

**Cấu trúc layout:**
```
QMainWindow
  └── centralWidget (QWidget)
        └── QVBoxLayout
              ├── NavBar (QFrame)
              └── body (QHBoxLayout)
                    ├── SideBar (QFrame, optional)
                    └── content_area (QWidget, stretch=1)
```

**Các method quan trọng:**

| Method | Mô tả |
|---|---|
| `load_content_ui(filename)` | Load file `.ui` vào `content_area`, trả về widget |
| `_connect_sidebar()` | Kết nối 6 nút sidebar (override trong từng controller) |
| `_transfer_window_state(target)` | Sao chép trạng thái cửa sổ sang window mới |
| `_go_overview()` | Navigate đến OverviewAdminController |
| `_go_bookings()` | Navigate đến BookingOverviewController |
| `_go_edit(preselect_room)` | Navigate đến EditRoomController |
| `_go_users()` | Navigate đến UsersManagementController |
| `_logout()` | Xác nhận rồi quay về Login |
| `_quit()` | Xác nhận rồi thoát ứng dụng |
| `_show_booking_management()` | Mở dialog BookingApproval (Admin) |
| `_approve(booking_id, dlg)` | Duyệt booking, sinh mật khẩu tủ |
| `_reject(booking_id, dlg)` | Từ chối booking, nhập lý do |

---

## 6. Tầng dữ liệu (Models)

### 6.1 Cơ sở dữ liệu

**File:** `datasets/smartlocker.db` (SQLite)
**Khởi tạo:** `database.init_db()` — tạo bảng nếu chưa tồn tại
**Kết nối:** `database.get_connection()` — trả về `sqlite3.Connection` với `row_factory = sqlite3.Row`

### 6.2 Schema

#### Bảng `users`

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `username` | TEXT | UNIQUE NOT NULL |
| `password` | TEXT | NOT NULL (SHA-256 hash) |
| `role` | TEXT | CHECK IN ('admin', 'user') |

#### Bảng `rooms`

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `room_id` | TEXT | UNIQUE NOT NULL (ví dụ: "A101") |
| `room_type` | TEXT | NOT NULL (ví dụ: "Lecture Room") |
| `capacity` | INTEGER | NOT NULL DEFAULT 50 |
| `status` | TEXT | CHECK IN ('Available', 'Occupied', 'Full', 'Cleaning') |

> **Lưu ý:** Trạng thái `Full` trong DB là trạng thái tĩnh do admin set. Trạng thái `Full` động (tính từ bookings) được tính trong `get_display_status()` ở `room_card.py` và không lưu vào DB.

#### Bảng `bookings`

| Cột | Kiểu | Ràng buộc |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | FOREIGN KEY → users(id) |
| `room_id` | INTEGER | FOREIGN KEY → rooms(id) |
| `session` | TEXT | NOT NULL (ví dụ: "Session 1 (07:00 – 09:30)") |
| `reason` | TEXT | NOT NULL |
| `status` | TEXT | CHECK IN ('Pending', 'Approved', 'Rejected') DEFAULT 'Pending' |
| `reject_reason` | TEXT | NULL |
| `locker_password` | TEXT | NULL (6 chữ số, sinh khi Approved) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

### 6.3 user_model.py

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `hash_password(password)` | `str` | `str` | SHA-256 hex digest |
| `authenticate(username, password)` | `str, str` | `dict \| None` | Xác thực đăng nhập |
| `get_all_users()` | — | `list[dict]` | Lấy tất cả user (id, username, role) |
| `create_user(username, password, role)` | `str, str, str` | `bool` | Tạo user mới |
| `update_user(user_id, username, password, role)` | `int, str, str, str` | `bool` | Cập nhật user (password rỗng = không đổi) |
| `delete_user(user_id)` | `int` | — | Xóa user |

### 6.4 room_model.py

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `get_all_rooms()` | — | `list[dict]` | Lấy tất cả phòng |
| `get_rooms_by_status(status)` | `str` | `list[dict]` | Lọc theo status |
| `search_rooms(keyword)` | `str` | `list[dict]` | Tìm theo room_id hoặc room_type (LIKE) |
| `create_room(room_id, room_type, capacity, status)` | `str, str, int, str` | `bool` | Tạo phòng mới |
| `update_room(pk, room_id, room_type, capacity, status)` | `int, str, str, int, str` | `bool` | Cập nhật phòng |
| `delete_room(pk)` | `int` | — | Xóa phòng |

### 6.5 booking_model.py

| Hàm | Tham số | Trả về | Mô tả |
|---|---|---|---|
| `get_bookings_by_user(user_id)` | `int` | `list[dict]` | Booking của 1 user, JOIN rooms |
| `get_all_bookings()` | — | `list[dict]` | Tất cả booking, JOIN rooms + users |
| `create_booking(user_id, room_id, session, reason)` | `int, int, str, str` | `bool` | Tạo booking (status=Pending) |
| `update_booking(booking_id, session, reason)` | `int, str, str` | — | Cập nhật booking Pending |
| `cancel_booking(booking_id)` | `int` | — | Xóa booking Pending |
| `approve_booking(booking_id)` | `int` | `str` | Duyệt, trả về mật khẩu 6 số |
| `reject_booking(booking_id, reason)` | `int, str` | — | Từ chối, lưu lý do |
| `delete_booking(booking_id)` | `int` | — | Xóa booking (admin) |
| `admin_update_booking(booking_id, session, reason, status)` | `int, str, str, str` | — | Admin cập nhật toàn bộ |
| `get_dashboard_stats()` | — | `dict` | Thống kê: total_rooms, total_bookings, pending, approved, rejected |
| `get_bookings_by_room(room_pk)` | `int` | `list[dict]` | Booking Pending/Approved của 1 phòng |
| `get_all_users_simple()` | — | `list[dict]` | id + username cho combobox |

---

## 7. Tầng Widget

### 7.1 NavBar (`widgets/navbar.py`)

Load từ `ui/navbar.ui`. Hiển thị ở đầu mọi màn hình (trừ Login).

**Thuộc tính:**
- `btnRole`: nút hiển thị vai trò (Admin/User), click để mở BookingApproval (admin) hoặc BookingHistory (user)
- `lineEditSearch`: ô tìm kiếm, ẩn nếu `show_search=False`

### 7.2 SideBar (`widgets/sidebar.py`)

Load từ `ui/sidebar.ui`. Chỉ hiển thị ở màn hình Admin.

**Các nút:**
- `btnOverview` → Room Overview
- `btnBookings` → Booking Overview
- `btnEdit` → Room Management
- `btnUsers` → Users Management
- `btnLogout` → Đăng xuất (có xác nhận)
- `btnQuit` → Thoát ứng dụng (có xác nhận)

### 7.3 RoomCard (`widgets/room_card.py`)

Tạo card phòng kích thước cố định **200×110px**.

**Cấu trúc card:**
```
┌─────────────────────────────┐
│ A101              Available │  ← Header: room_id + badge trạng thái
│ Lecture Room · 50 seats     │  ← Loại phòng + sức chứa
│ ─────────────────────────── │  ← Divider
│      ●  ●  ●  ●             │  ← Session dots (xanh/cam/xám)
└─────────────────────────────┘
```

**Màu session dots:**
- Xanh lá `#4CAF50`: session đã Approved
- Cam `#FF9800`: session đang Pending
- Xám `#D0D0D0`: session trống

**Hàm `get_display_status(room)`:**
Tính trạng thái hiển thị động. Nếu cả 4 session đều có booking Pending hoặc Approved → trả về `"Full"`. Ngược lại trả về `room["status"]`.

**Hằng số `SESSIONS`:**
```python
SESSIONS = [
    ("Session 1", "07:00 – 09:30"),
    ("Session 2", "09:45 – 12:15"),
    ("Session 3", "12:30 – 15:00"),
    ("Session 4", "15:15 – 17:45"),
]
```
Session lưu vào DB dạng string: `"Session 1 (07:00 – 09:30)"`.

---

## 8. Controllers

### 8.1 MainWindowController (`controllers/main_window.py`)

Màn hình đăng nhập. Kế thừa `QMainWindow` trực tiếp (không qua BaseWindow).

**Tính năng:**
- Background `images/background.jpg` scale-to-cover (giữ tỉ lệ, không méo) qua mixin `_BgWidget` inject vào `centralwidget` tại runtime
- Toggle hiển thị mật khẩu (eye icon)
- Xác thực email + password, kiểm tra role khớp radio button
- Flag `_logging_in` chống double-submit khi nhấn Enter
- F11 toggle fullscreen

**Luồng đăng nhập:**
```
Nhập email + password → authenticate() → kiểm tra role → _open_dashboard(user)
```

### 8.2 OverviewAdminController (`controllers/overview_admin.py`)

Dashboard chính của Admin. Hiển thị lưới room cards.

**Tính năng:**
- Filter: All / Available / Occupied / Full / Cleaning
- Tìm kiếm theo room_id hoặc room_type
- Grid responsive: tự tính số cột dựa trên `content_area.width()`, reflow khi resize
- Chuột phải vào card → context menu "Edit Room" → nhảy đến Room Management với phòng được chọn sẵn
- Navbar btnRole → BookingApproval dialog

**Responsive grid:**
```python
cols = max(1, available_width // (card_width + spacing))
```

### 8.3 OverviewUsersController (`controllers/overview_users.py`)

Dashboard của User. Không có sidebar.

**Tính năng:**
- Filter + search phòng (giống admin)
- Chuột phải vào card → "Book Room" → mở BookingDialog với phòng được chọn sẵn
- Navbar btnRole → BookingHistory dialog
- Bottom bar: btnBooking, btnLogout, btnQuit

**BookingDialog:**
- Chọn phòng (comboRoom), chọn session (multi-select toggle buttons), nhập lý do
- Session đã có booking Pending/Approved → disabled + tooltip "This session is already booked"
- Khi đổi phòng trong combo → tự cập nhật lại trạng thái session buttons
- Submit → `create_booking()` cho từng session được chọn

### 8.4 EditRoomController (`controllers/edit_room.py`)

Quản lý phòng (Room Management). Load `RoomManagement.ui`.

**Tính năng:**
- Bảng danh sách phòng (Room ID, Room Type, Capacity, Status)
- Click dòng → điền form bên trái
- CRUD: Create, Update, Delete (có xác nhận)
- Import CSV: chọn file `.csv` với cột `room_id, room_type, capacity, status`
- Tìm kiếm realtime

**Format CSV:**
```csv
room_id,room_type,capacity,status
A101,Lecture Room,50,Available
B202,Lab,30,Available
```

**Preselect:** Khi navigate từ context menu "Edit Room", controller nhận `preselect_room` và tự điền form + highlight dòng tương ứng trong bảng.

### 8.5 BookingOverviewController (`controllers/booking_overview.py`)

Quản lý booking (Booking Overview). Load `BookingOverview.ui`.

**Tính năng:**
- Bảng tất cả booking (User, Room, Type, Session, Reason, Status, Locker Password, Edit, Delete)
- Filter theo status (All Status / Pending / Approved / Rejected)
- Tìm kiếm theo username, room_name, session
- Nút Edit → dialog chỉnh sửa (có thêm comboStatus)
- Nút Delete → xác nhận rồi xóa
- Nút "+ Add" → dialog tạo booking mới

**Dialog booking** được build bằng code thuần (không dùng file `.ui`), dùng `QFormLayout` với các trường: User, Room, Session, Reason (và Status khi edit).

### 8.6 UsersManagementController (`controllers/users_management.py`)

Quản lý người dùng. Load `Users.ui`.

**Tính năng:**
- Bảng danh sách user (Username, Password ẩn "••••••", Role)
- Click dòng → điền form
- CRUD: Create, Update, Delete
- Không cho phép xóa tài khoản đang đăng nhập
- Tìm kiếm theo username hoặc role

---

## 9. Giao diện (UI Files)

### Bảng ánh xạ UI ↔ Controller

| File .ui | Controller / Widget | Mô tả |
|---|---|---|
| `Login.ui` | `MainWindowController` | Màn hình đăng nhập |
| `navbar.ui` | `NavBar` | Header chung |
| `sidebar.ui` | `SideBar` | Sidebar Admin |
| `OverviewAdmin.ui` | `OverviewAdminController` | Dashboard Admin |
| `OverviewUsers.ui` | `OverviewUsersController` | Dashboard User |
| `BookingDialog.ui` | `OverviewUsersController` | Dialog đặt phòng |
| `BookingApproval.ui` | `BaseWindow` | Dialog duyệt booking (Admin) |
| `BookingHistory.ui` | `OverviewUsersController` | Dialog lịch sử booking (User) |
| `BookingOverview.ui` | `BookingOverviewController` | Trang quản lý booking |
| `RoomManagement.ui` | `EditRoomController` | Trang quản lý phòng |
| `Users.ui` | `UsersManagementController` | Trang quản lý user |

### Palette màu chính

| Màu | Hex | Dùng cho |
|---|---|---|
| Navy | `#1F4F82` | Primary (navbar, nút chính, border focus) |
| Navy đậm | `#163D66` | Hover state |
| Xanh lá | `#4CAF50` | Approved, Available |
| Cam | `#FF9800` | Pending, Full |
| Đỏ | `#F44336` | Rejected, Occupied |
| Xanh dương | `#2196F3` | Cleaning |
| Nền sidebar | `#DCE3EC` | SideBar background |
| Nền content | `#F5F8FC` | Content area background |

---

## 10. Bảo mật

- **Mật khẩu người dùng**: hash SHA-256 trước khi lưu vào DB, không lưu plaintext
- **Mật khẩu tủ locker**: 6 chữ số ngẫu nhiên (`random.choices(string.digits, k=6)`), sinh khi admin duyệt booking
- **SQL Injection**: toàn bộ query dùng parameterized statements (`?` placeholder), không nối chuỗi trực tiếp
- **Foreign keys**: bật `PRAGMA foreign_keys = ON` để đảm bảo toàn vẹn dữ liệu
- **Phân quyền**: kiểm tra role tại màn hình login, mỗi role chỉ truy cập được controller tương ứng

---

## 11. Các hằng số và quy ước

### Trạng thái phòng (`rooms.status`)

| Giá trị | Ý nghĩa |
|---|---|
| `Available` | Phòng trống, có thể đặt |
| `Occupied` | Đang sử dụng |
| `Full` | Tất cả session đã được đặt (tính động) |
| `Cleaning` | Đang vệ sinh |

### Trạng thái booking (`bookings.status`)

| Giá trị | Ý nghĩa |
|---|---|
| `Pending` | Chờ duyệt |
| `Approved` | Đã duyệt, có mật khẩu tủ |
| `Rejected` | Bị từ chối, có lý do |

### Session

Lưu vào DB dạng: `"Session N (HH:MM – HH:MM)"`

| Session | Thời gian |
|---|---|
| Session 1 | 07:00 – 09:30 |
| Session 2 | 09:45 – 12:15 |
| Session 3 | 12:30 – 15:00 |
| Session 4 | 15:15 – 17:45 |

---

## 12. Luồng nghiệp vụ chính

### 12.1 Đặt phòng (User)

```
User chọn phòng Available
  → Chuột phải "Book Room" hoặc nhấn "Booking"
  → BookingDialog mở
  → Chọn session (session đã book bị disabled)
  → Nhập lý do
  → Submit → create_booking() → status = Pending
  → Admin nhận thông báo trong BookingApproval
```

### 12.2 Duyệt booking (Admin)

```
Admin nhấn nút "Admin" trên navbar
  → BookingApproval dialog mở
  → Xem danh sách booking Pending
  → Nhấn "Approve" → approve_booking()
      → status = Approved
      → sinh mật khẩu 6 số ngẫu nhiên
      → hiển thị mật khẩu cho admin
  → Nhấn "Reject" → nhập lý do → reject_booking()
      → status = Rejected
      → lưu reject_reason
```

### 12.3 Import phòng từ CSV (Admin)

```
Room Management → "Import CSV"
  → Chọn file .csv
  → Đọc từng dòng: room_id, room_type, capacity, status
  → Validate: room_id và room_type không được rỗng, capacity phải là số
  → create_room() cho từng dòng hợp lệ
  → Báo cáo: số dòng imported / skipped / chi tiết lỗi
```

---

## 13. Ghi chú phát triển

- Tất cả file `.ui` nằm trong `ui/`, load bằng `uic.loadUi(path, widget)`
- Controllers không tự tạo layout — chỉ gọi `self.load_content_ui("TenFile.ui")` và thao tác với widget trả về qua `self.ui`
- Models là pure functions, không có class, không giữ state
- `get_display_status()` và logic "Full" động không được lưu vào DB — chỉ tính tại runtime để hiển thị
- Khi thêm màn hình mới: tạo file `.ui`, tạo controller kế thừa `BaseWindow`, thêm navigation method vào `BaseWindow`, thêm nút vào `sidebar.ui`
