# SmartLocker UEL

Phần mềm quản lý đặt phòng và tủ thiết bị cho Trường Đại học Kinh tế Luật (UEL).
Xây dựng bằng Python + PyQt6, lưu trữ dữ liệu SQLite.

---

## Yêu cầu

- Python 3.10+
- PyQt6

```bash
pip install PyQt6
```

---

## Chạy ứng dụng

```bash
# Lần đầu: tạo DB và seed dữ liệu mẫu
python3 seed.py

# Khởi động
python3 main.py
```

> Chạy lại `seed.py` bất cứ lúc nào để reset toàn bộ dữ liệu về mặc định.

---

## Tài khoản mặc định

| Vai trò | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| User | `sv001@st.uel.edu.vn` | `123456` |
| User | `sv002@st.uel.edu.vn` | `123456` |

---

## Chức năng

### Admin (5 tab)

| Tab | Chức năng |
|---|---|
| Overview | Dashboard thống kê (tổng phòng, booking, Pending/Approved/Rejected) + grid phòng responsive |
| Bookings | Xem danh sách booking, duyệt (tự động sinh mật khẩu tủ 6 số), từ chối (kèm lý do), xem chi tiết, export CSV |
| Rooms | CRUD phòng, filter theo trạng thái (All/Available/Occupied), tìm kiếm, import/export CSV |
| Users | CRUD tài khoản, filter theo role (All/Admin/User), xem lịch sử booking của từng user, import/export CSV |
| Devices | Quản lý thiết bị theo phòng, filter theo trạng thái, cấp/reset mật khẩu tủ khóa, import/export CSV |

### User (Sinh viên / Giảng viên)

- Xem grid phòng với 3 nhóm filter độc lập: trạng thái, sức chứa (≤50 / 100+), ca học (Sáng 06–12 / Chiều 12–17 / Tối 17–22)
- Xem bảng availability theo từng slot 30 phút (06:00–22:00) trước khi đặt
- Đặt phòng với kiểm tra xung đột thời gian tự động
- Xem lịch sử booking, chỉnh sửa hoặc hủy booking đang Pending
- Nhận mật khẩu tủ thiết bị khi booking được Approved
- Xem lý do từ chối nếu booking bị Rejected

---

## Cấu trúc dự án

```
SmartLockUEL/
├── main.py                     # Entry point
├── database.py                 # Kết nối SQLite, khởi tạo schema
├── seed.py                     # Reset DB và tạo dữ liệu mẫu
├── controllers/
│   ├── main_window.py          # Màn hình đăng nhập
│   ├── overview_admin.py       # Dashboard Admin
│   ├── overview_users.py       # Trang chủ User (đặt phòng)
│   ├── booking_overview.py     # Quản lý booking (Admin)
│   ├── edit_room.py            # Quản lý phòng (Admin)
│   ├── users_management.py     # Quản lý tài khoản (Admin)
│   └── device_management.py    # Quản lý thiết bị (Admin)
├── models/
│   ├── user_model.py           # CRUD users, SHA-256 hash
│   ├── room_model.py           # CRUD rooms
│   ├── booking_model.py        # CRUD bookings, conflict detection
│   └── device_model.py         # CRUD devices, password management
├── widgets/
│   ├── base_window.py          # Base class (NavBar + SideBar + ScrollArea)
│   ├── navbar.py               # Thanh điều hướng trên
│   ├── sidebar.py              # Sidebar Admin
│   └── room_card.py            # Card hiển thị phòng, tính trạng thái Full động
├── ui/                         # File giao diện Qt Designer (.ui)
├── images/                     # SVG icons
└── datasets/
    └── smartlocker.db          # Cơ sở dữ liệu SQLite
```

---

## Cơ sở dữ liệu

SQLite với 4 bảng:

| Bảng | Các cột chính |
|---|---|
| `users` | `id`, `username`, `password` (SHA-256), `role` (admin/user) |
| `rooms` | `id`, `room_id`, `room_type`, `capacity`, `status` (Available/Occupied) |
| `bookings` | `id`, `user_id`, `room_id`, `session`, `reason`, `status`, `locker_password`, `reject_reason`, `created_at` |
| `devices` | `id`, `room_id`, `device_name`, `cabinet_password`, `status` (Active/Inactive/Maintenance) |

**Ghi chú:**
- Trạng thái `Full` được tính **động** tại runtime — không lưu vào DB
- `session` lưu dạng `"YYYY-MM-DD | HH:mm - HH:mm"`
- Mật khẩu tủ (`locker_password`) được sinh tự động 6 chữ số khi Admin duyệt booking

---

## Công nghệ

- Python 3.10+ · PyQt6 · SQLite 3 · Qt Designer (.ui)
- Mật khẩu: SHA-256 (hashlib)
- Icons: PNG
- AI Assistant: Claude (Anthropic) — hỗ trợ phát triển qua Claude Code

---

## Vai trò trong dự án

Tôi tham gia dự án với vai trò hỗ trợ kỹ thuật cho nhóm sinh viên. Công việc bao gồm hướng dẫn kiến trúc ứng dụng, review code, hỗ trợ xử lý lỗi và tối ưu giao diện trong quá trình nhóm phát triển phần mềm.
