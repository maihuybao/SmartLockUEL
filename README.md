# SmartLockerUEL

Phần mềm đặt lịch mượn phòng - Trường Đại Học Kinh Tế Luật (UEL)

## Yêu cầu

- Python 3.10+
- PyQt6

```bash
pip install PyQt6
```

## Chạy ứng dụng

```bash
# Tạo dữ liệu mẫu (chạy lần đầu)
python3 seed.py

# Khởi động ứng dụng
python3 main.py
```

## Tài khoản mặc định

| Vai trò | Username            | Password |
| ------- | ------------------- | -------- |
| Admin   | admin               | admin123 |
| User    | sv001@st.uel.edu.vn | 123456   |

## Cấu trúc dự án

```
Source/
├── main.py                     # Entry point
├── database.py                 # Kết nối SQLite + khởi tạo schema
├── seed.py                     # Dữ liệu mẫu
├── controllers/
│   ├── main_window.py          # Màn hình đăng nhập
│   ├── overview_admin.py       # Dashboard Admin + duyệt booking
│   ├── overview_users.py       # Dashboard User + đặt phòng
│   ├── edit_room.py            # CRUD phòng (Admin)
│   └── users_management.py     # CRUD user (Admin)
├── models/
│   ├── user_model.py           # Model User (authenticate, CRUD)
│   ├── room_model.py           # Model Room (CRUD, search, filter)
│   └── booking_model.py        # Model Booking (CRUD, approve/reject)
├── ui/                         # Giao diện Qt Designer (.ui)
├── images/                     # Icons và assets
└── datasets/
    └── smartlocker.db          # Cơ sở dữ liệu SQLite
```

## Chức năng

### User (Sinh viên / Giảng viên)

- Đăng nhập bằng email/mật khẩu
- Xem danh sách phòng (lọc theo trạng thái, Search)
- Đặt phòng (chọn buổi Sáng/Chiều/Tối, nhập lý do)
- Xem lịch sử đặt phòng, hủy booking chưa duyệt
- Nhận mật khẩu tủ thiết bị khi booking được duyệt

### Admin (Administrator)

- Quản lý phòng: thêm, sửa, xóa
- Quản lý user: thêm, sửa, xóa
- Duyệt / từ chối yêu cầu đặt phòng
- Dashboard thống kê (tổng phòng, booking, tỷ lệ duyệt)

## Cơ sở dữ liệu

SQLite với 3 bảng:

- **users**: id, username, password (SHA-256), role (admin/user)
- **rooms**: id, room_id, room_type, capacity, status
- **bookings**: id, user_id, room_id, session, reason, status, reject_reason, locker_password, created_at

## Công nghệ

- Python 3 + PyQt6
- SQLite3
- Qt Designer (.ui files)
