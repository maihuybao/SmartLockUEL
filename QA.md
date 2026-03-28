# Câu hỏi & Trả lời bảo vệ đồ án — SmartLockUEL

---

## Câu 1: Trong tình huống đặt phòng, làm thế nào để quản lý một phòng được mượn theo nhiều khung giờ khác nhau trong ngày? Cấu trúc mô hình hướng đối tượng xử lý như thế nào?

### Khái niệm cốt lõi

Phòng học là một **tài nguyên chia sẻ theo thời gian** — tại một thời điểm chỉ có một người dùng, nhưng trong một ngày có thể được nhiều người dùng ở các khung giờ khác nhau. Vì vậy hệ thống không quản lý "ai đang dùng phòng" mà quản lý **lịch sử các khoảng thời gian đã được đặt** của phòng đó.

Mỗi lần đặt phòng (Booking) ghi lại đầy đủ:
- **Ai** đặt (sinh viên / giảng viên)
- **Phòng nào** được đặt
- **Ngày nào**, **từ giờ nào đến giờ nào**

Khi có yêu cầu đặt mới, hệ thống so sánh khung giờ mới với toàn bộ các booking đã có của phòng đó trong cùng ngày. Nếu không có khoảng thời gian nào chồng lên nhau thì cho phép đặt.

---

### Cách hệ thống hiện tại hoạt động

Phòng không bị "khóa" theo ca — trạng thái phòng trong bảng `rooms` chỉ phản ánh tình trạng vật lý (`Available`, `Occupied`). Toàn bộ việc quản lý thời gian mượn được xử lý qua bảng `bookings`, mỗi bản ghi lưu 3 trường thời gian riêng biệt:

```
rooms                         bookings
──────────────────            ─────────────────────────────────────────────────────
id=1  room_id="A101"          id=1  room_id=1  date=2026-03-28  06:00→12:00  user=A  Approved
      status="Available"      id=2  room_id=1  date=2026-03-28  13:00→17:00  user=B  Approved
                              id=3  room_id=1  date=2026-03-29  08:00→10:00  user=C  Pending
```

Khi B muốn đặt A101 buổi chiều cùng ngày với A, hệ thống gọi hàm `has_conflict()` để kiểm tra:

```python
# Thuật toán phát hiện xung đột: 2 khoảng thời gian chồng nhau khi ns < be AND ne > bs
ns, ne = 13:00, 17:00   # B muốn đặt  (new start, new end)
bs, be = 06:00, 12:00   # A đang giữ  (booked start, booked end)

13:00 < 12:00  →  False  →  không xung đột  →  cho phép B đặt
```

Vì điều kiện `False`, B được phép đặt. Cùng một phòng A101 có thể có nhiều booking khác nhau trong ngày miễn các khung giờ không chồng lên nhau.

---

### Mô hình hướng đối tượng tương đương


```
┌─────────────────────────────────┐         ┌──────────────────────────────────┐
│              Room               │  1    * │            Booking               │
├─────────────────────────────────┤─────────┤──────────────────────────────────┤
│ - id: int                       │         │ - id: int                        │
│ - room_id: str                  │         │ - room: Room                     │
│ - room_type: str                │         │ - user: User                     │
│ - capacity: int                 │         │ - date: date                     │
│ - bookings: list[Booking]       │         │ - time_start: time               │
├─────────────────────────────────┤         │ - time_end: time                 │
│ + is_available(date, start, end)│         │ - status: BookingStatus          │
│   └─ duyệt bookings, gọi        │         │ - locker_password: str           │
│      conflicts_with() từng cái  │         ├──────────────────────────────────┤
│ + get_status(date) → str        │         │ + conflicts_with(other) → bool   │
│   └─ tính động: còn slot trống? │         │   └─ self.start < other.end      │
│ + add_booking(booking) → bool   │         │      AND self.end > other.start  │
└─────────────────────────────────┘         │ + approve() → str                │
                                            │ + reject(reason)                 │
                                            │ + cancel()                       │
┌─────────────────────────────────┐         └──────────────────────────────────┘
│              User               │
├─────────────────────────────────┤
│ - id: int                       │
│ - username: str                 │
│ - role: Role                    │
│ - bookings: list[Booking]       │
├─────────────────────────────────┤
│ + book(room, date, start, end)  │
│   └─ room.is_available() → True │
│      → Booking() → thêm vào DB  │
│ + get_history() → list[Booking] │
└─────────────────────────────────┘
```

### Luồng xử lý: A đặt sáng, B đặt chiều

```
User_A.book(room_A101, "2026-03-28", "06:00", "12:00")
    ├─ room_A101.is_available(...)
    │       └─ bookings rỗng → không xung đột → True
    └─ tạo Booking(A, A101, 06:00→12:00) → status: Pending

User_B.book(room_A101, "2026-03-28", "13:00", "17:00")
    ├─ room_A101.is_available(...)
    │       └─ so với booking A: 13:00 < 12:00 → False → không xung đột → True
    └─ tạo Booking(B, A101, 13:00→17:00) → status: Pending

room_A101.bookings = [
    Booking(A, 06:00→12:00, Approved),
    Booking(B, 13:00→17:00, Approved)
]

room_A101.get_status("2026-03-28")
    └─ còn slot 17:00→22:00 trống → "Available"
    └─ tất cả 32 slot 30 phút đã kín → "Full"
```

---

## Câu 2: Để bảo mật thông tin đăng nhập của người dùng và quản trị hệ thống, đề xuất kỹ thuật mã hóa dữ liệu như thế nào?

### Khái niệm Hash và SHA-256

**Hash** (băm) là quá trình chuyển đổi một chuỗi dữ liệu đầu vào có độ dài bất kỳ thành một chuỗi đầu ra có độ dài cố định thông qua một hàm toán học. Hàm băm có 3 tính chất quan trọng:

- **Một chiều:** không thể tính ngược từ hash ra dữ liệu gốc
- **Tất định:** cùng đầu vào luôn cho cùng đầu ra
- **Nhạy cảm với thay đổi:** chỉ thay đổi 1 ký tự đầu vào sẽ tạo ra hash hoàn toàn khác

**SHA-256** (Secure Hash Algorithm 256-bit) là một hàm băm thuộc họ SHA-2 do NIST chuẩn hóa, luôn tạo ra chuỗi 256 bit (64 ký tự hex) bất kể độ dài đầu vào:

```
"admin123"  →  240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a
"admin124"  →  b3c2cfd73f4476b01c38a3b3e6a0e9e0e9451c99c76d6b3f1b93e7d71b7c8f2
```

Chỉ thay `3` thành `4` nhưng hash thay đổi hoàn toàn — đây là tính chất **avalanche effect**.

---

### Cách hệ thống hiện tại bảo vệ mật khẩu

Dự án đang dùng **SHA-256** để băm mật khẩu trước khi lưu vào cơ sở dữ liệu:

```python
# models/user_model.py
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Khi đăng nhập: so sánh hash, không bao giờ lưu mật khẩu gốc
def authenticate(username, password):
    conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
```

Mật khẩu lưu trong DB trông như sau — không thể đọc ngược lại thành mật khẩu gốc:

```
admin123  →  240be518...a9e8f9b  (64 ký tự hex)
```

---

### Tại sao dự án chọn SHA-256?

SHA-256 có sẵn trong thư viện chuẩn Python (`hashlib`), không cần cài thêm gói ngoài — phù hợp với yêu cầu đơn giản hóa môi trường chạy của đồ án. Với một hệ thống triển khai thực tế quy mô lớn hơn, việc chuyển sang `bcrypt` là bước nâng cấp bảo mật cần thiết.
