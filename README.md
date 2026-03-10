# SmartLocker UEL

Phần mềm đặt lịch mượn phòng — Trường Đại học Kinh tế Luật (UEL)

## Yêu cầu

- Python 3.10+
- PyQt6

```bash
pip install PyQt6
```

## Chạy ứng dụng

```bash
# Tạo dữ liệu mẫu (chạy lần đầu hoặc khi muốn reset DB)
python3 seed.py

# Khởi động ứng dụng
python3 main.py
```

## Tài khoản mặc định

| Vai trò | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| User | `sv001@st.uel.edu.vn` | `123456` |

## Cấu trúc dự án

```
SmartLockUEL/
├── main.py                     # Entry point
├── database.py                 # Kết nối SQLite + khởi tạo schema
├── seed.py                     # Reset DB và tạo dữ liệu mẫu
├── controllers/
│   ├── main_window.py          # Màn hình đăng nhập
│   ├── overview_admin.py       # Trang chủ Admin (Dashboard + grid phòng)
│   ├── overview_users.py       # Trang chủ User (grid phòng + đặt phòng)
│   ├── booking_overview.py     # Quản lý booking (Admin)
│   ├── edit_room.py            # CRUD phòng (Admin)
│   ├── users_management.py     # CRUD user (Admin)
│   └── device_management.py    # Quản lý thiết bị (Admin)
├── models/
│   ├── user_model.py
│   ├── room_model.py
│   ├── booking_model.py
│   └── device_model.py
├── widgets/
│   ├── base_window.py          # Base class cho mọi màn hình
│   ├── navbar.py
│   ├── sidebar.py
│   └── room_card.py            # Card hiển thị phòng
├── ui/                         # File giao diện Qt Designer (.ui)
├── images/                     # Icons và assets
└── datasets/
    └── smartlocker.db          # Cơ sở dữ liệu SQLite
```

## Chức năng

### User (Sinh viên / Giảng viên)

- Đăng nhập bằng email/mật khẩu
- Xem grid phòng với 3 nhóm filter độc lập: trạng thái, sức chứa (≤50 / 100+), ca học (Sáng/Chiều/Tối)
- Xem bảng availability theo giờ khi đặt phòng (06:00–22:00)
- Đặt phòng với kiểm tra xung đột thời gian tự động
- Xem lịch sử booking, chỉnh sửa hoặc hủy booking chưa duyệt
- Nhận mật khẩu tủ thiết bị khi booking được duyệt
- Xem lý do từ chối nếu booking bị reject

### Admin

- Dashboard thống kê: tổng phòng, tổng booking, Pending / Approved / Rejected
- Quản lý phòng: CRUD + import CSV
- Quản lý booking: duyệt (tự động sinh mật khẩu tủ), từ chối (kèm lý do), export CSV
- Quản lý user: CRUD
- Quản lý thiết bị: thêm/xóa thiết bị, cấp/reset mật khẩu tủ khóa

## Cơ sở dữ liệu

SQLite với 4 bảng:

- **users**: `id`, `username`, `password` (SHA-256), `role`
- **rooms**: `id`, `room_id`, `room_type`, `capacity`, `status`
- **bookings**: `id`, `user_id`, `room_id`, `session`, `reason`, `status`, `reject_reason`, `locker_password`, `created_at`
- **devices**: `id`, `room_id`, `device_name`, `cabinet_password`, `status`

## Công nghệ

- Python 3.10+ · PyQt6 · SQLite 3 · Qt Designer (.ui files)
