# SmartLocker UEL — Câu hỏi bảo vệ đồ án

---

## 1. Tổng quan dự án

**Q: Dự án này giải quyết vấn đề gì thực tế?**
> Số hóa quy trình đặt phòng học tại UEL — thay thế việc đăng ký thủ công bằng phần mềm desktop, tự động cấp mật khẩu tủ khóa khi booking được duyệt, giúp quản lý phòng và thiết bị hiệu quả hơn.

**Q: Tại sao chọn ứng dụng desktop thay vì web?**
> Phù hợp với môn học Kỹ thuật lập trình, PyQt6 cho phép xây dựng giao diện phong phú mà không cần backend server hay hosting. Triển khai đơn giản — chỉ cần cài Python và chạy.

**Q: Tại sao chọn SQLite thay vì MySQL hay PostgreSQL?**
> SQLite không cần cài đặt server riêng, lưu toàn bộ dữ liệu trong một file `.db`, phù hợp với ứng dụng desktop local. Đủ đáp ứng quy mô đồ án và dễ demo.

**Q: Hệ thống có bao nhiêu loại người dùng, phân quyền như thế nào?**
> Hai role: **Admin** và **User**. Admin có toàn quyền quản lý phòng, booking, user, thiết bị. User chỉ xem phòng, đặt phòng và quản lý booking của chính mình.

---

## 2. Kiến trúc hệ thống

**Q: Dự án dùng mô hình kiến trúc gì?**
> MVC đơn giản hóa:
> - **Model** — pure functions trong `models/`, không có class, không giữ state
> - **View** — file `.ui` thiết kế bằng Qt Designer
> - **Controller** — class Python kế thừa `BaseWindow`, load `.ui` và xử lý sự kiện

**Q: BaseWindow là gì, tại sao cần nó?**
> `BaseWindow` là lớp cơ sở tái sử dụng layout NavBar + SideBar + ScrollArea cho tất cả màn hình. Controller chỉ cần gọi `self.load_content_ui("TenFile.ui")` để inject giao diện riêng vào `content_area`, tránh lặp code layout ở mỗi màn hình.

**Q: Tại sao Model chỉ dùng pure functions, không dùng class?**
> Đơn giản hóa — mỗi function độc lập, không giữ state, dễ đọc và debug. Mỗi function tự mở/đóng kết nối DB, trả về `dict` hoặc `list[dict]`. Phù hợp với quy mô đồ án.

**Q: Khi chuyển màn hình, dữ liệu user được truyền như thế nào?**
> `current_user` dict được truyền qua constructor của mỗi controller. `BaseWindow` lưu vào `self.current_user` và truyền tiếp khi navigate sang màn hình khác.

**Q: Luồng điều hướng giữa các màn hình hoạt động như thế nào?**
> Mỗi lần chuyển màn hình: tạo controller mới → `_transfer_window_state()` để giữ kích thước/vị trí cửa sổ → `new_controller.show()` → `self.close()`. Không dùng stack hay router.

**Q: Tại sao file `.ui` được load lúc runtime thay vì compile thành Python?**
> Dùng `uic.loadUi()` cho phép chỉnh sửa giao diện trong Qt Designer mà không cần recompile. Linh hoạt hơn trong quá trình phát triển, thay đổi UI không ảnh hưởng logic Python.

**Q: Signal và Slot trong PyQt6 là gì, dự án dùng như thế nào?**
> Signal/Slot là cơ chế event của Qt. Khi user click nút, widget phát ra signal `clicked`. Controller kết nối signal đó với một hàm xử lý (slot) bằng `.connect()`. Ví dụ: `self.ui.pushButtonApprove.clicked.connect(self._approve_booking)`.

---

## 3. Cơ sở dữ liệu

**Q: Cơ sở dữ liệu có bao nhiêu bảng, quan hệ như thế nào?**
> 4 bảng:
> - `users` — thông tin tài khoản
> - `rooms` — danh sách phòng
> - `bookings` — lịch đặt phòng (FK đến `users` và `rooms`)
> - `devices` — thiết bị khóa thông minh (FK đến `rooms`)

**Q: Mật khẩu người dùng được lưu như thế nào?**
> Hash SHA-256 bằng `hashlib.sha256(password.encode()).hexdigest()`. Không bao giờ lưu plain text. Khi đăng nhập, hash input rồi so sánh với hash trong DB.

**Q: Trạng thái "Full" của phòng được lưu vào DB không?**
> Không. `Full` được tính **động** tại runtime trong `_is_full_today()` — kiểm tra xem tất cả slot 30 phút trong 06:00–22:00 đã bị đặt hết chưa. DB chỉ lưu `Available` và `Occupied`.

**Q: Tại sao dùng TEXT để lưu thời gian booking thay vì kiểu DATETIME?**
> Format `"YYYY-MM-DD | HH:mm - HH:mm"` lưu cả ngày lẫn khoảng giờ trong một trường, dễ parse và hiển thị trực tiếp trên UI. Đánh đổi là không dùng được SQL date functions, nhưng với quy mô đồ án thì chấp nhận được.

**Q: Foreign key có được enforce không?**
> Có. Mỗi kết nối đều bật `PRAGMA foreign_keys = ON` trong `get_connection()`.

**Q: Tại sao `locker_password` và `reject_reason` cho phép NULL?**
> Vì chúng chỉ có giá trị ở trạng thái cụ thể: `locker_password` chỉ sinh khi Approved, `reject_reason` chỉ có khi Rejected. Ở trạng thái Pending cả hai đều NULL.

**Q: Schema được khởi tạo như thế nào?**
> Hàm `init_db()` trong `database.py` dùng `CREATE TABLE IF NOT EXISTS` — chỉ tạo bảng nếu chưa tồn tại. Gọi tự động khi ứng dụng khởi động lần đầu.

---

## 4. Tính năng & Logic nghiệp vụ

**Q: Thuật toán kiểm tra xung đột booking hoạt động như thế nào?**
> Dùng interval overlap: hai khoảng `[ns, ne)` và `[bs, be)` xung đột khi `ns < be AND ne > bs`. Convert giờ sang phút để so sánh số nguyên. Lấy tất cả booking Pending/Approved của phòng trong ngày đó rồi kiểm tra từng cái.

**Q: Khi user chỉnh sửa booking, làm sao tránh conflict với chính booking đó?**
> Hàm `has_conflict()` có tham số `exclude_id` — bỏ qua booking đang được edit khi kiểm tra overlap. Nếu không có tham số này, booking sẽ conflict với chính nó.

**Q: Mật khẩu tủ khóa được sinh như thế nào, khi nào?**
> `random.choices(string.digits, k=6)` — chuỗi 6 chữ số ngẫu nhiên. Sinh tự động khi Admin nhấn Approve, lưu vào `bookings.locker_password`, hiển thị cho User trong Booking History.

**Q: Filter theo ca học (Morning/Afternoon/Evening) hoạt động như thế nào?**
> `_has_free_slot()` kiểm tra xem phòng có ít nhất 1 slot 30 phút trống trong khoảng giờ của ca đó hôm nay không. Morning = 06:00–12:00, Afternoon = 12:00–17:00, Evening = 17:00–22:00.

**Q: Bảng availability trong BookingDialog hiển thị gì, màu sắc có ý nghĩa gì?**
> 16 cột tương ứng 16 giờ (06–21h). Mỗi ô:
> - Xanh lá = trống, có thể đặt
> - Vàng = có booking đang chờ duyệt (Pending)
> - Đỏ = đã được duyệt (Approved), không thể đặt

**Q: Tại sao grid phòng tự thay đổi số cột khi resize cửa sổ?**
> `resizeEvent` và `showEvent` tính lại `cols = available_width // (card_width + spacing)` mỗi khi cửa sổ thay đổi kích thước, đảm bảo giao diện responsive.

**Q: Admin có thể xóa chính mình không?**
> Không. `UsersManagementController` kiểm tra `user_id == current_user["id"]` trước khi xóa và hiển thị thông báo lỗi nếu cố tình xóa.

**Q: Trạng thái booking có thể chuyển đổi như thế nào?**
> Chỉ theo một chiều: `Pending` → `Approved` hoặc `Pending` → `Rejected`. Không thể đảo ngược. User chỉ có thể hủy (xóa) booking khi còn Pending.

**Q: Import CSV phòng hoạt động như thế nào?**
> Đọc file CSV với các cột `room_id, room_type, capacity, status`. Mỗi dòng gọi `create_room()`. Báo cáo số dòng imported thành công và số dòng bị skip (trùng room_id hoặc lỗi).

**Q: Export CSV booking lấy dữ liệu từ đâu?**
> Lấy từ danh sách đang hiển thị trên bảng sau khi áp dụng filter và search — không phải toàn bộ DB. Admin thấy gì thì export đó.

---

## 5. Bảo mật

**Q: Ứng dụng xử lý bảo mật mật khẩu như thế nào?**
> Mật khẩu hash SHA-256 trước khi lưu. Khi đăng nhập, hash input rồi so sánh với hash trong DB — không bao giờ so sánh plain text hay decrypt.

**Q: Có thể SQL injection không?**
> Không. Tất cả query dùng parameterized statements với `?` placeholder, không nối chuỗi trực tiếp vào SQL. Ví dụ: `conn.execute("SELECT * FROM users WHERE username=?", (username,))`.

**Q: Phân quyền được kiểm soát ở đâu?**
> Tại màn hình đăng nhập: sau khi xác thực, kiểm tra `user["role"]` có khớp với radio button đã chọn không. Sau đó mỗi controller chỉ expose chức năng phù hợp với role — Admin và User có màn hình hoàn toàn khác nhau.

**Q: Nếu user đoán được URL hoặc tên màn hình, có thể truy cập trái phép không?**
> Không. Đây là desktop app, không có URL. Mỗi controller nhận `current_user` qua constructor — không có cách nào khởi tạo `OverviewAdminController` mà không có user object hợp lệ từ quá trình đăng nhập.

---

## 6. Hạn chế & Hướng phát triển

**Q: Hạn chế lớn nhất của dự án là gì?**
> - SQLite không phù hợp cho nhiều người dùng đồng thời (concurrent writes)
> - Không có notification real-time khi booking được duyệt/từ chối
> - Mật khẩu tủ khóa chỉ là số ngẫu nhiên, chưa tích hợp phần cứng thực tế
> - Không có tính năng quên mật khẩu hay đăng ký tài khoản

**Q: Nếu mở rộng lên web, cần thay đổi gì?**
> Tách Model thành REST API (Flask/FastAPI), thay SQLite bằng PostgreSQL, giữ nguyên business logic trong `models/`, xây dựng lại View bằng React hoặc Vue. Controller sẽ trở thành API endpoints.

**Q: Tại sao không dùng ORM như SQLAlchemy?**
> Raw SQL đủ cho quy mô đồ án, dễ hiểu hơn khi báo cáo, không cần học thêm framework. Với 4 bảng đơn giản, ORM sẽ là over-engineering.

**Q: Làm sao để scale hệ thống nếu UEL có hàng nghìn sinh viên?**
> Chuyển sang PostgreSQL hoặc MySQL, thêm connection pooling, cache kết quả query thường dùng, tách thành client-server architecture với REST API.

**Q: Có thể thêm tính năng gì để hoàn thiện hơn?**
> - Gửi email/notification khi booking được duyệt
> - Tích hợp API phần cứng khóa thông minh thực tế
> - Báo cáo thống kê theo tuần/tháng với biểu đồ
> - Tính năng đặt phòng định kỳ (recurring booking)
> - Xác thực 2 bước (2FA)
