# SmartLocker UEL — Technical Documentation

**Version:** 3.0
**Date:** 2026-03-10
**Platform:** Python 3.10+, PyQt6, SQLite 3

---

## 1. Project Overview

### 1.1 Purpose

SmartLocker UEL is a desktop application for managing room bookings and smart locker devices at the University of Economics and Law (UEL). It digitizes the room reservation process, enabling students and lecturers to book rooms online while administrators manage approvals, room inventory, users, and locker devices.

### 1.2 Scope

| Actor | Capabilities |
|---|---|
| Admin | View room grid with dashboard stats, manage bookings (approve/reject/CRUD + CSV import/export), manage rooms (CRUD + CSV), manage users (CRUD + CSV + view user bookings), manage devices (CRUD + CSV + password generation) |
| User | View available rooms with 3 filter groups (status/capacity/session), submit booking requests with availability table, view booking history, edit/cancel pending bookings, view booking details |

### 1.3 Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.10+ |
| GUI Framework | PyQt6 |
| UI Design | Qt Designer (.ui files), loaded via `PyQt6.uic.loadUi()` |
| Database | SQLite 3 — file at `datasets/smartlocker.db` |
| Password Hashing | SHA-256 via `hashlib` |
| Icons | PNG files (15 files in `images/`) |
| Data Import/Export | CSV via Python stdlib `csv` module |

### 1.4 Project Structure

```
SmartLockUEL/
├── main.py                    # Application entry point
├── database.py                # SQLite connection, schema init
├── seed.py                    # DB reset and sample data seeding
├── CLAUDE.md                  # AI assistant instructions
├── TECHNICAL_DOCS.md          # This file
│
├── controllers/
│   ├── main_window.py         # Login screen
│   ├── overview_admin.py      # Admin dashboard — room grid + stats
│   ├── overview_users.py      # User home — room grid + booking + history
│   ├── booking_overview.py    # Admin — booking management
│   ├── edit_room.py           # Admin — room CRUD
│   ├── users_management.py    # Admin — user CRUD
│   └── device_management.py   # Admin — device management
│
├── models/
│   ├── user_model.py          # 6 functions
│   ├── room_model.py          # 6 functions
│   ├── booking_model.py       # 16 functions
│   └── device_model.py        # 7 functions
│
├── widgets/
│   ├── base_window.py         # Base class for all admin/user screens
│   ├── navbar.py              # Top navigation bar widget
│   ├── sidebar.py             # Left sidebar widget (admin only)
│   └── room_card.py           # Room card widget + dynamic Full status
│
├── ui/                        # 18 Qt Designer .ui files
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
├── images/                    # 15 image assets (PNG + JPG)
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
    └── smartlocker.db         # SQLite database file (auto-created)
```

### 1.5 Installation & Running

```bash
# Install dependency
pip install PyQt6

# First run: reset DB and seed sample data
python3 seed.py

# Start the application
python3 main.py
```

### 1.6 Default Accounts

After running `seed.py`, 10 user accounts are created:

| Username | Password | Role |
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

## 2. System Architecture

### 2.1 Architectural Pattern

The application follows a **simplified MVC** pattern without a formal framework:

- **Model** — pure functions in `models/`, no classes, no state. Each function accepts and returns plain `dict` or `list[dict]`.
- **View** — `.ui` files designed in Qt Designer, loaded at runtime via `uic.loadUi()`.
- **Controller** — Python classes inheriting `BaseWindow`, loading a `.ui` file into `content_area` and wiring up signals/slots.

### 2.2 Navigation Flow

```
main.py
  └── MainWindowController  (Login.ui)
        ├── [role = admin] ──> OverviewAdminController  (OverviewAdmin.ui)
        │                          ├── Sidebar: Overview   ──> (current page)
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
                                   │     ├── Edit          ──> BookingDialog  (QDialog, edit mode)
                                   │     └── Cancel        ──> delete Pending booking
                                   ├── Button: Log Out     ──> MainWindowController
                                   └── Button: Quit        ──> QApplication.quit()
```

**Screen transition pattern:**
```python
new_controller = TargetController(self.current_user)
self._transfer_window_state(new_controller)   # preserve size/position/fullscreen
new_controller.show()
self.close()
```

### 2.3 BaseWindow Layout

`BaseWindow` (`widgets/base_window.py`) is the base class for all controllers except `MainWindowController`. It builds the following layout automatically:

```
QMainWindow
  └── centralWidget (QWidget)
        └── QVBoxLayout (margins=0, spacing=0)
              ├── NavBar  (QFrame — top bar with logo + search + role button)
              └── body    (QHBoxLayout, margins=0, spacing=0)
                    ├── SideBar  (QFrame — left nav, optional)
                    └── QScrollArea (widgetResizable=True, no frame)
                          └── content_area  (QWidget)
                                └── QVBoxLayout (margins=0)
                                      └── [UI loaded by controller via load_content_ui()]
```

Controllers call `self.load_content_ui("FileName.ui")` to inject their screen into `content_area`. The `QScrollArea` wrapper ensures content is scrollable when the window is too small.

### 2.4 UI File — Controller Mapping (18 files)

| .ui File | Controller / Location | Widget Root | Description |
|---|---|---|---|
| `Login.ui` | `controllers/main_window.py` | QMainWindow | Login screen with background image |
| `MainWindow.ui` | `widgets/base_window.py` | — | (Not used directly, layout built in code) |
| `navbar.ui` | `widgets/navbar.py` | QFrame | Top navigation bar |
| `sidebar.ui` | `widgets/sidebar.py` | QFrame | Left sidebar with 7 buttons |
| `OverviewAdmin.ui` | `controllers/overview_admin.py` | QWidget | Admin dashboard: stats + room grid |
| `OverviewUsers.ui` | `controllers/overview_users.py` | QWidget | User home: 3 filter groups + room grid |
| `BookingDialog.ui` | inline in `overview_users.py` | QDialog | Create/edit booking form |
| `BookingHistory.ui` | inline in `overview_users.py` | QDialog | User booking history table |
| `BookingDetails.ui` | inline in `overview_users.py` + `booking_overview.py` | QDialog | Read-only booking detail view |
| `BookingManagement.ui` | `controllers/booking_overview.py` | QWidget | Admin booking management table |
| `AdminBookingDialog.ui` | inline in `booking_overview.py` | QDialog | Admin create/edit/reject booking form |
| `RoomManagement.ui` | `controllers/edit_room.py` | QWidget | Admin room management table |
| `RoomDialog.ui` | inline in `edit_room.py` | QDialog | Add/edit room form |
| `Users.ui` | `controllers/users_management.py` | QWidget | Admin user management table |
| `UserDialog.ui` | inline in `users_management.py` | QDialog | Add/edit user form |
| `UserBookingsView.ui` | inline in `users_management.py` | QDialog | View bookings of a specific user |
| `DeviceManagement.ui` | `controllers/device_management.py` | QWidget | Admin device management table |
| `DeviceDialog.ui` | inline in `device_management.py` | QDialog | Add/edit device form |

---

## 3. Database Design

### 3.1 Entity Relationship Diagram

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

### 3.2 Table: `users`

```sql
CREATE TABLE IF NOT EXISTS users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL,
    role     TEXT    NOT NULL CHECK(role IN ('admin', 'user'))
)
```

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `username` | TEXT | UNIQUE, NOT NULL | Login username (email format for students/lecturers) |
| `password` | TEXT | NOT NULL | SHA-256 hex digest of the plain-text password |
| `role` | TEXT | CHECK IN ('admin','user') | Access level |

### 3.3 Table: `rooms`

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

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `room_id` | TEXT | UNIQUE, NOT NULL | Human-readable room code (e.g. `A101`) |
| `room_type` | TEXT | NOT NULL | Category: Classroom, Lab, Meeting Room, Study Room |
| `capacity` | INTEGER | DEFAULT 50 | Maximum number of occupants |
| `status` | TEXT | CHECK, DEFAULT 'Available' | Current room status |

> **Note:** The `Full` status is computed **dynamically** at runtime in `widgets/room_card.py:get_display_status()`. It is never written to the database. A room is considered Full when every 30-minute slot between 06:00 and 22:00 is covered by at least one active (Pending or Approved) booking for today. When filtering by "Available", rooms that are dynamically Full are excluded from results.

### 3.4 Table: `bookings`

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

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `user_id` | INTEGER | FK -> users(id) | Booking owner |
| `room_id` | INTEGER | FK -> rooms(id) | Target room |
| `date` | TEXT | NOT NULL | Booking date: `"YYYY-MM-DD"` |
| `time_start` | TEXT | NOT NULL | Start time: `"HH:mm"` |
| `time_end` | TEXT | NOT NULL | End time: `"HH:mm"` |
| `reason` | TEXT | NOT NULL | Purpose of booking |
| `status` | TEXT | CHECK, DEFAULT 'Pending' | Approval state |
| `reject_reason` | TEXT | NULL | Populated when status = Rejected |
| `locker_password` | TEXT | NULL | 6-digit code generated when Approved |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

### 3.5 Table: `devices`

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

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `room_id` | INTEGER | FK -> rooms(id) | Room this device belongs to |
| `device_name` | TEXT | NOT NULL | Device label (e.g. `Smart Lock A101`) |
| `cabinet_password` | TEXT | NULL | 6-digit locker PIN |
| `status` | TEXT | CHECK, DEFAULT 'Active' | Operational state |

---

## 4. Data Layer — Models

All model files contain **pure functions only** — no classes, no shared state. Each function opens a connection, executes a query, closes the connection, and returns a `dict` or `list[dict]`. Foreign key enforcement is enabled via `PRAGMA foreign_keys = ON` in `database.py:get_connection()`.

### 4.1 `models/user_model.py` (6 functions)

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `hash_password(password)` | `str` | `str` | Returns SHA-256 hex digest |
| `authenticate(username, password)` | `str, str` | `dict \| None` | Hashes password, SELECT WHERE match; returns user row or None |
| `get_all_users()` | — | `list[dict]` | All users (id, username, role only) |
| `create_user(username, password, role)` | `str, str, str` | `bool` | Inserts new user; returns False on duplicate username |
| `update_user(user_id, username, password, role)` | `int, str, str, str` | `bool` | Updates user; empty password = keep existing hash |
| `delete_user(user_id)` | `int` | — | Deletes user by id |

### 4.2 `models/room_model.py` (6 functions)

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `get_all_rooms()` | — | `list[dict]` | All rooms (SELECT *) |
| `get_rooms_by_status(status)` | `str` | `list[dict]` | Filter by status value |
| `search_rooms(keyword)` | `str` | `list[dict]` | LIKE search on room_id and room_type |
| `create_room(room_id, room_type, capacity, status)` | `str, str, int, str` | `bool` | Insert new room; default status="Available" |
| `update_room(pk, room_id, room_type, capacity, status)` | `int, str, str, int, str` | `bool` | Update room by primary key |
| `delete_room(pk)` | `int` | — | Delete room by primary key |

### 4.3 `models/booking_model.py` (16 functions)

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `get_bookings_by_user(user_id)` | `int` | `list[dict]` | All bookings for a user (JOIN rooms), ORDER BY created_at DESC |
| `get_all_bookings()` | — | `list[dict]` | All bookings (JOIN rooms + users), ORDER BY created_at DESC |
| `create_booking(user_id, room_id, date, time_start, time_end, reason)` | `int, int, str, str, str, str` | `bool` | Create booking with status=Pending |
| `update_booking(booking_id, date, time_start, time_end, reason)` | `int, str, str, str, str` | — | Update time/reason (Pending only) |
| `cancel_booking(booking_id)` | `int` | — | DELETE booking (Pending only) |
| `_generate_locker_password()` | — | `str` | Internal: random 6-digit string |
| `approve_booking(booking_id)` | `int` | `str` | Set Approved, generate 6-digit locker_password, return it |
| `reject_booking(booking_id, reason)` | `int, str` | — | Set Rejected, store reject_reason |
| `get_dashboard_stats()` | — | `dict` | Counts: total_rooms, total_bookings, pending, approved, rejected |
| `delete_booking(booking_id)` | `int` | — | Hard delete (Admin, any status) |
| `admin_update_booking(booking_id, date, time_start, time_end, reason, status)` | `int, str, str, str, str, str` | — | Admin full update (date + time + reason + status) |
| `get_all_users_simple()` | — | `list[dict]` | SELECT id, username ORDER BY username |
| `get_bookings_by_room(room_pk)` | `int` | `list[dict]` | Active bookings (Pending/Approved) for a room — returns date, time_start, time_end, status |
| `get_bookings_by_room_date(room_pk, date_str)` | `int, str` | `list[dict]` | Active bookings for a room on a specific date (WHERE date = ?) |
| `_to_minutes(t)` | `str` | `int` | Convert "HH:mm" to minutes since midnight |
| `has_conflict(room_pk, date_str, start_str, end_str, exclude_id)` | `int, str, str, str, int\|None` | `bool` | Check time overlap; exclude_id skips one booking (for edit) |

**Conflict detection algorithm:**

Two time intervals `[ns, ne)` and `[bs, be)` overlap when:
```
ns < be  AND  ne > bs
```
This is the standard interval overlap test. The function converts `"HH:mm"` strings to minutes-since-midnight via `_to_minutes()` before comparing.

### 4.4 `models/device_model.py` (7 functions)

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `get_all_devices()` | — | `list[dict]` | All devices (JOIN rooms for room_id as room_name), ORDER BY room_id, device_name |
| `search_devices(keyword)` | `str` | `list[dict]` | LIKE search on room_id, device_name, status |
| `create_device(room_id, device_name, status)` | `int, str, str` | `bool` | Insert new device; default status="Active" |
| `update_device_password(device_id, new_password)` | `int, str` | — | Update cabinet_password |
| `update_device_status(device_id, status)` | `int, str` | — | Update device status |
| `delete_device(device_id)` | `int` | — | Delete device |
| `generate_password()` | — | `str` | Return random 6-digit string |

---

## 5. Controllers

### 5.1 `MainWindowController` (`controllers/main_window.py`)

Inherits `QMainWindow` directly (not `BaseWindow`). Loads `Login.ui`.

**Key methods:**

| Method | Description |
|---|---|
| `__init__()` | Load Login.ui, init_db(), setup background/UI/signals, min size 1000x600 |
| `_setup_background()` | Dynamic class `BgCentral` with `_BgWidget` mixin, paints `background.jpg` scale-to-cover |
| `_make_login_responsive()` | Card login with white background `rgba(255,255,255,0.92)`, border-radius 12px |
| `_setup_ui()` | Set logo pixmap, eye icons for password toggle, input text color styling |
| `_connect_signals()` | pushButtonLogin, btnTogglePassword, returnPressed on both inputs |
| `_toggle_password()` | Toggle EchoMode Normal/Password, swap eye_open/eye_closed icon |
| `_handle_login()` | Validate inputs -> authenticate() -> check role matches radio button -> _open_dashboard() |
| `_toggle_fullscreen()` | F11 shortcut handler |
| `_open_dashboard(user)` | role='admin' -> OverviewAdminController, role='user' -> OverviewUsersController |

**Login flow:**
1. User enters username + password, selects role radio button (Admin / User)
2. `authenticate(username, password)` hashes the input with SHA-256 and compares against DB
3. If credentials match but role does not match the radio button -> error
4. On success -> instantiate the appropriate controller, show it, close login

**`_BgWidget` mixin:** Overrides `paintEvent` to draw `background.jpg` scaled with `KeepAspectRatioByExpanding` + `SmoothTransformation`, centered on the widget.

### 5.2 `OverviewAdminController` (`controllers/overview_admin.py`)

Inherits `BaseWindow`. Loads `OverviewAdmin.ui`. Parameters: `show_search=True, show_sidebar=True`.

**Key methods:**

| Method | Description |
|---|---|
| `__init__(user)` | Load UI, connect signals, load stats + rooms |
| `_connect_sidebar()` | Override: pushButtonOverview -> lambda: None (current page) |
| `_connect_signals()` | Filter buttons (All/Available/Occupied/Full) + navbar search |
| `_load_rooms()` | Combine keyword search + status filter + exclude Full from Available |
| `_render_room_cards(rooms)` | Store `_rooms_data`, call `_reflow_grid()` |
| `_reflow_grid()` | Calculate cols, clear layout, add cards in grid pattern |
| `showEvent(event)` / `resizeEvent(event)` | Call `_reflow_grid()` for responsive layout |
| `_create_room_card(room)` | Delegate to `create_room_card(room, on_context=...)` |
| `_on_card_context(room, global_pos)` | Context menu: "Edit Room" -> `_go_edit(preselect_room=room)` |
| `_apply_filter(status)` | Set `_current_filter`, reload rooms |
| `_on_search()` | Reload rooms with current keyword |
| `_load_stats()` | `get_dashboard_stats()` -> set 5 stat labels |

**Dashboard stats displayed:** Total Rooms, Total Bookings, Pending, Approved, Rejected.

**Available filter logic:** When filter is "Available", rooms where `get_display_status(room) == "Full"` are excluded from results. This ensures dynamically-full rooms don't appear as available.

### 5.3 `OverviewUsersController` (`controllers/overview_users.py`)

Inherits `BaseWindow`. Loads `OverviewUsers.ui`. Parameters: `show_search=True, show_sidebar=False`.

**Three independent filter groups:**

| Group | Options | State variable |
|---|---|---|
| Status | All / Available / Occupied / Full | `_current_filter` |
| Capacity | All / <=50 / 100+ | `_capacity_filter` |
| Session | All / Morning (06-12) / Afternoon (12-17) / Evening (17-22) | `_time_filter` |

**Key methods:**

| Method | Description |
|---|---|
| `__init__(user)` | Init 3 filter states to "All", load UI, connect signals, load rooms |
| `_connect_signals()` | 12 filter buttons + navbar search + History/Booking/Logout/Quit buttons |
| `_apply_filter(status)` / `_apply_capacity(cap)` / `_apply_time(session)` | Set filter state, reload rooms |
| `_load_rooms()` | Chain: keyword/status -> exclude Full from Available -> capacity -> time filter |
| `_has_free_slot(room_pk, date_str, range_start, range_end)` | Static: check if any 30-min slot is free in range |
| `_render_room_cards(rooms)` / `_reflow_grid()` | Same responsive grid pattern as Admin |
| `_on_card_context(room, global_pos)` | Context menu: "Book Room" -> `_open_booking_dialog(room)` |
| `_open_booking_dialog(preselect_room)` | Load BookingDialog.ui, populate combos, validate, create_booking() |
| `_refresh_availability(dlg)` | Build 16-column availability table (06-21h), color-coded |
| `_show_history()` | Load BookingHistory.ui, comboFilter, populate table |
| `_populate_history(dlg, filter_text)` | Fill 10-column table with action buttons per row |
| `_view_booking(booking_id, parent_dlg)` | Load BookingDetails.ui, hide User field |
| `_edit_booking(booking_id, history_dlg)` | Load BookingDialog.ui in edit mode, disable comboRoom |
| `_cancel_booking(booking_id, dlg)` | Confirm -> cancel_booking() -> refresh |

**Time ranges constant:**
```python
TIME_RANGES = {
    "Morning":   (360, 720),    # 06:00 - 12:00
    "Afternoon": (720, 1020),   # 12:00 - 17:00
    "Evening":   (1020, 1320),  # 17:00 - 22:00
}
```

**Booking Dialog features:**
- Room combo populated with Available rooms only
- Date picker: minimum = today
- Time edits: start 06:00-21:59, end 06:01-22:00
- Availability table: 16 columns (hours 06-21), color-coded:
  - Green (`#A5D6A7`) = free
  - Amber (`#FFE082`) = Pending booking
  - Red (`#EF9A9A`) = Approved booking
- Validation: purpose required, end > start, hours within 06:00-22:00, no conflict

**Booking History features:**
- Filter by status (All Status / Pending / Approved / Rejected)
- 10 columns: Room, Type, Date, Start, End, Reason, Status (colored), Locker Password, Reject Reason (red), Actions
- Actions column (fixed 100px): View (always) + Edit + Cancel (Pending only)
- Action buttons use PNG icons: `view.png`, `edit.png`, `delete.png`

### 5.4 `BookingOverviewController` (`controllers/booking_overview.py`)

Inherits `BaseWindow`. Loads `BookingManagement.ui`. Parameters: `show_search=False, show_sidebar=True`.

**Key methods:**

| Method | Description |
|---|---|
| `__init__(user)` | Load UI, connect signals, load table |
| `_connect_sidebar()` | pushButtonBookings -> lambda: None (current page) |
| `_connect_signals()` | Filter buttons + lineEditSearch + Add/Import/Export buttons |
| `_load_table()` | get_all_bookings() -> filter status + keyword -> fill table |
| `_make_icon_btn(icon_file, tooltip, bg, hover, slot)` | Helper: create styled 22x22 icon button |
| `_make_actions_widget(booking_id, status)` | View (always) + Approve/Reject (Pending) + Edit + Delete |
| `_view_booking(booking_id)` | Load BookingDetails.ui, show User field |
| `_approve_booking_inline(booking_id)` | approve_booking() -> show password in QMessageBox |
| `_reject_booking_inline(booking_id)` | _build_booking_dialog(reject_mode=True) -> reject_booking() |
| `_add_booking()` | _build_booking_dialog() -> create_booking() |
| `_edit_booking(booking_id)` | _build_booking_dialog(booking) -> admin_update_booking() |
| `_delete_booking(booking_id)` | Confirm -> delete_booking() |
| `_import_csv()` | CSV columns: username, room_id, date, start_time, end_time, reason |
| `_export_csv()` | Export filtered view: User, Room, Type, Date, Start Time, End Time, Purpose, Status, Locker Password |
| `_build_booking_dialog(booking, reject_mode)` | Load AdminBookingDialog.ui, populate combos |

**Table columns (10):** User, Room, Type, Date, Start, End, Purpose, Status (colored), Locker Password, Actions (fixed 130px).

**AdminBookingDialog modes:**
- **Add mode:** Hide labelStatus, comboStatus, labelRejectReason, editRejectReason
- **Edit mode:** Show all fields except reject reason
- **Reject mode:** Disable all fields except editRejectReason; hide status combo

### 5.5 `EditRoomController` (`controllers/edit_room.py`)

Inherits `BaseWindow`. Loads `RoomManagement.ui`. Parameters: `show_search=False, show_sidebar=True`.

**Key methods:**

| Method | Description |
|---|---|
| `__init__(user, preselect_room=None)` | Load UI, connect signals, load table, preselect if provided |
| `_connect_sidebar()` | pushButtonEdit -> lambda: None (current page) |
| `_connect_signals()` | Filter (All/Available/Occupied) + lineEditSearch + Add + CSV buttons |
| `_apply_filter()` | Filter by status radio + keyword (room_id, room_type) |
| `_populate_table(rooms)` | 5 columns: room_id, room_type, capacity, status (colored), actions (fixed 72px) |
| `_make_actions_widget(room)` | Edit + Delete buttons (22x22 with PNG icons) |
| `_preselect(room)` | Select row matching room_id in table |
| `_build_room_dialog(room)` | Load RoomDialog.ui, pre-fill if editing |
| `_add_room()` | Validate room_id, room_type, capacity (int) -> create_room() |
| `_edit_room(room)` | Validate -> update_room() |
| `_delete_room(room_pk)` | Confirm -> delete_room() |
| `_import_csv()` | CSV columns: room_id, room_type, capacity, status |
| `_export_csv()` | Export: room_id, room_type, capacity, status |

**Status colors in table:** Available=#4CAF50, Occupied=#FF9800, Cleaning=#2196F3, Full=#F44336.

### 5.6 `UsersManagementController` (`controllers/users_management.py`)

Inherits `BaseWindow`. Loads `Users.ui`. Parameters: `show_search=False, show_sidebar=True`.

**Key methods:**

| Method | Description |
|---|---|
| `__init__(user)` | Load UI, connect signals, load table |
| `_connect_sidebar()` | pushButtonUsers -> lambda: None (current page) |
| `_connect_signals()` | Filter (All/Admin/User) + lineEditSearch + Add + CSV buttons |
| `_apply_filter()` | Filter by role radio + keyword (username) |
| `_populate_table(users)` | 3 columns: username, role (colored), actions (fixed 100px) |
| `_make_actions_widget(user)` | View Bookings (purple) + Edit (blue) + Delete (red) buttons |
| `_build_user_dialog(user)` | Load UserDialog.ui, pre-fill if editing |
| `_add_user()` | Validate username + password -> create_user() |
| `_edit_user(user)` | Validate username -> update_user() (password optional) |
| `_delete_user(user_id)` | Guard: cannot delete self -> Confirm -> delete_user() |
| `_view_user_bookings(user)` | Load UserBookingsView.ui, 7-column table |
| `_import_csv()` | CSV columns: username, password, role |
| `_export_csv()` | Export: username, role (no password) |

**Role colors:** admin=#E91E63 (pink), user=#4CAF50 (green).

**UserBookingsView table (7 columns):** Room, Type, Date, Start, End, Reason, Status (colored).

### 5.7 `DeviceManagementController` (`controllers/device_management.py`)

Inherits `BaseWindow`. Loads `DeviceManagement.ui`. Parameters: `show_search=False, show_sidebar=True`.

**Key methods:**

| Method | Description |
|---|---|
| `__init__(user)` | Load UI, connect signals, load table |
| `_connect_sidebar()` | pushButtonDevices -> lambda: None (current page) |
| `_connect_signals()` | Filter (All/Active/Inactive/Maintenance) + lineEditSearch + Add + CSV buttons |
| `_apply_filter()` | Filter by status radio + keyword (room_name, device_name) |
| `_populate_table(devices)` | 5 columns: room, device_name, cabinet_password, status (colored), actions (fixed 100px) |
| `_make_actions_widget(device)` | Edit + Delete buttons |
| `_build_device_dialog(device)` | Load DeviceDialog.ui, populate comboRoom |
| `_add_device()` | Validate device_name -> create_device() |
| `_edit_device(device)` | update_device_status() always + update_device_password() if new_pw |
| `_delete_device(device_id)` | Confirm -> delete_device() |
| `_import_csv()` | CSV columns: room_id, device_name, status |
| `_export_csv()` | Export: room, device_name, cabinet_password, status |

**DeviceDialog modes:**
- **Add mode:** Hide labelPw + pwWidget (no password field)
- **Edit mode:** Show editPw + btnGenPw (refresh.png icon), click generates random 6-digit password

**Status colors:** Active=#4CAF50, Inactive=#9E9E9E, Maintenance=#FF9800.

---

## 6. Widgets

### 6.1 `BaseWindow` (`widgets/base_window.py`)

Base class for all controllers except `MainWindowController`. Minimum size 800x500, default 1200x800.

| Method | Parameters | Description |
|---|---|---|
| `__init__` | `user, role_text="Admin", show_search=False, show_sidebar=True, title="SmartLocker UEL"` | Builds NavBar + optional SideBar + ScrollArea layout |
| `_connect_sidebar()` | — | Wires 7 sidebar buttons to navigation methods. Override in subclass to set current page to `lambda: None` |
| `load_content_ui(filename)` | `str` | Loads `ui/<filename>` into `content_area` via `uic.loadUi()`, returns the widget |
| `_go_overview()` | — | Navigate to `OverviewAdminController` |
| `_go_bookings()` | — | Navigate to `BookingOverviewController` |
| `_go_edit(preselect_room=None)` | `dict\|None` | Navigate to `EditRoomController` |
| `_go_users()` | — | Navigate to `UsersManagementController` |
| `_go_devices()` | — | Navigate to `DeviceManagementController` |
| `_transfer_window_state(target)` | `QMainWindow` | Copy fullscreen/maximized/size+position to target window |
| `_toggle_fullscreen()` | — | F11 handler: toggle fullscreen/normal |
| `_logout()` | — | Confirm dialog -> return to `MainWindowController` |
| `_quit()` | — | Static. Confirm dialog -> `QApplication.quit()` |

### 6.2 `NavBar` (`widgets/navbar.py`)

Loaded from `navbar.ui`. A `QFrame` widget containing the top navigation bar.

| Element | Description |
|---|---|
| `btnRole` | Displays role text ("Admin" or "User") with role-specific icon |
| `lineEditSearch` | Real-time search input, hidden when `show_search=False` |

**Icon logic:**
- `role_text == "Admin"` -> `admin.png` icon
- Any other role_text -> `user.png` icon
- Icon size: 20x20

### 6.3 `SideBar` (`widgets/sidebar.py`)

Loaded from `sidebar.ui`. A `QFrame` widget containing navigation buttons for admin screens.

**Buttons (7):**
- `pushButtonOverview` — Dashboard
- `pushButtonBookings` — Booking Management
- `pushButtonEdit` — Room Management
- `pushButtonUsers` — User Management
- `pushButtonDevices` — Device Management
- `pushButtonLogOut` — Log Out
- `pushButtonQuit` — Quit Application

Each controller overrides `_connect_sidebar()` to set its own button to `lambda: None` (no-op for current page) while connecting the rest to navigation methods.

### 6.4 `room_card` (`widgets/room_card.py`)

Module-level functions for creating room card widgets and computing dynamic status.

**Constants:**
```python
OP_START = 6 * 60   # 360 minutes (06:00)
OP_END   = 22 * 60  # 1320 minutes (22:00)

STATUS_COLORS = {"Available": "#4CAF50", "Occupied": "#F44336", "Full": "#FF9800"}
STATUS_BG     = {"Available": "#E8F5E9", "Occupied": "#FFEBEE", "Full": "#FFF3E0"}
```

**Functions:**

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `_to_minutes(t)` | `str` | `int` | Convert "HH:mm" to minutes since midnight |
| `_is_full_today(room_pk)` | `int` | `bool` | Check if all 30-min slots (06:00-22:00) are booked today |
| `get_display_status(room)` | `dict` | `str` | If status=="Available" and _is_full_today() -> "Full", else room["status"] |
| `create_room_card(room, on_context)` | `dict, callable\|None` | `QWidget` | Create 200x110 card with border, header, type/capacity, booking count |

**Card layout:**
```
QWidget (200x110, border 2px solid {status_color}, border-radius 10px)
  └── QVBoxLayout (margins 12,10,12,10, spacing 6)
        ├── QHBoxLayout (header)
        │     ├── QLabel room_id (bold, 14px)
        │     ├── stretch
        │     └── QLabel status badge (colored, rounded, 10px)
        ├── QLabel "{room_type}  ·  {capacity} seats" (gray, 11px)
        ├── QFrame HLine (divider, #F0F0F0)
        └── QLabel "{N} active booking(s)" or "No active bookings" (centered)
```

**Context menu:** When `on_context` is provided, right-click triggers `on_context(room, global_pos)`.

---

## 7. Key Algorithms & Business Logic

### 7.1 Booking Conflict Detection

`models/booking_model.py:has_conflict()`

```python
def has_conflict(room_pk, date_str, start_str, end_str, exclude_id=None):
    bookings = get_bookings_by_room_date(room_pk, date_str)
    ns, ne = _to_minutes(start_str), _to_minutes(end_str)
    for b in bookings:
        if exclude_id is not None and b["id"] == exclude_id:
            continue
        bs, be = _to_minutes(b["time_start"]), _to_minutes(b["time_end"])
        if ns < be and ne > bs:   # standard interval overlap
            return True
    return False
```

The `exclude_id` parameter allows editing an existing booking without it conflicting with itself.

### 7.2 Dynamic "Full" Status

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

### 7.3 Available Filter Excludes Full

Both `OverviewAdminController` and `OverviewUsersController` apply this logic:

```python
if self._current_filter == "Available":
    rooms = [r for r in rooms if get_display_status(r) != "Full"]
```

This ensures that rooms which are technically "Available" in the database but dynamically Full (all slots booked today) are excluded when the user filters by "Available".

### 7.4 Responsive Grid Layout

Used in both Admin and User overview controllers:

```python
card_w  = 200
spacing = layout.horizontalSpacing() or 10
available = self.content_area.width() - 20
cols = max(1, available // (card_w + spacing))
```

Recalculated in both `resizeEvent` and `showEvent` to adapt to any window size. Cards are placed in a `QGridLayout` at position `(i // cols, i % cols)`. Stretch is added after the last row and column to push cards to the top-left.

### 7.5 Locker Password Generation

`models/booking_model.py:_generate_locker_password()`

```python
def _generate_locker_password():
    return "".join(random.choices(string.digits, k=6))
```

Called automatically when an admin approves a booking via `approve_booking()`. The 6-digit code is stored in `bookings.locker_password` and displayed to the admin immediately, and to the user in Booking History.

### 7.6 Session Time Filter (`_has_free_slot`)

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
        # add 30-min slots to booked set
        for slot in range(start_min, end_min, 30):
            booked.add(slot)
    return any(slot not in booked for slot in range(range_start, range_end, 30))
```

A room passes the session filter if it has **at least one free 30-minute slot** within the selected time range today.

### 7.7 Availability Table Rendering

`controllers/overview_users.py:_refresh_availability()`

The `BookingDialog` shows a 16-column table (one column per hour, 06-21). For each hour slot:

```
slot_s = hour * 60
slot_e = (hour + 1) * 60

For each active booking [bs, be, status]:
    if bs < slot_e and be > slot_s:   -> slot is occupied
        if status == "Approved" -> RED   (#EF9A9A)
        elif status == "Pending" -> AMBER (#FFE082)
    else                        -> GREEN (#A5D6A7)
```

Priority: Approved (red) takes precedence over Pending (amber) if both overlap the same hour.

---

## 8. Assets

### 8.1 Image Files (15 files in `images/`)

| File | Usage |
|---|---|
| `UEL_Logo.png` | Login screen logo (scaled to 120x120) |
| `background.jpg` | Login screen background (scale-to-cover via paintEvent) |
| `admin.png` | NavBar role icon for Admin users |
| `user.png` | NavBar role icon for non-Admin users |
| `eye_open.png` | Login password toggle — visible state |
| `eye_closed.png` | Login password toggle — hidden state |
| `approve.png` | Booking table action button — approve booking |
| `reject.png` | Booking table action button — reject booking |
| `edit.png` | Table action button — edit record (rooms, users, devices, bookings, history) |
| `delete.png` | Table action button — delete/cancel record |
| `view.png` | Table action button — view details (bookings, user bookings) |
| `search.png` | Search icon in management UI search bars (used as pixmap in .ui files) |
| `refresh.png` | Device dialog — generate new password button icon |
| `reload.png` | General reload/refresh icon |
| `settings.png` | Settings icon |

**Icon button pattern:** All table action buttons are 22x22 `QPushButton` with 14x14 icon size, styled with colored background + hover effect, border-radius 5-6px, no border.

---

## 9. Sample Data

Running `python3 seed.py` deletes the existing database and recreates it with the following data:

### 9.1 Users (10 total)

| Username | Password | Role |
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

### 9.2 Rooms (12 total)

| Room ID | Type | Capacity | Status |
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

### 9.3 Devices (12 total)

One Smart Lock device per room. All devices have auto-generated 6-digit passwords except:
- **Smart Lock C103**: `cabinet_password = NULL`, status = `Maintenance`
- **Smart Lock B102**: status = `Inactive`

### 9.4 Bookings (10 total)

| User | Room | Date | Time | Status | Notes |
|---|---|---|---|---|---|
| sv001@st.uel.edu.vn | A101 | 2026-03-10 | 07:00-09:30 | Approved | Has locker_password |
| sv002@st.uel.edu.vn | A101 | 2026-03-10 | 09:45-12:15 | Approved | Has locker_password |
| sv003@st.uel.edu.vn | B101 | 2026-03-10 | 12:30-15:00 | Pending | |
| sv004@st.uel.edu.vn | C101 | 2026-03-10 | 15:15-17:45 | Pending | |
| sv005@st.uel.edu.vn | A102 | 2026-03-11 | 07:00-09:30 | Rejected | Reason: "Room reserved for faculty use" |
| gv001@uel.edu.vn | B101 | 2026-03-11 | 09:45-12:15 | Approved | Has locker_password |
| sv001@st.uel.edu.vn | D101 | 2026-03-11 | 12:30-15:00 | Pending | |
| sv002@st.uel.edu.vn | E101 | 2026-03-12 | 07:00-09:30 | Approved | Has locker_password |
| sv003@st.uel.edu.vn | C102 | 2026-03-12 | 09:45-12:15 | Pending | |
| gv002@uel.edu.vn | A201 | 2026-03-12 | 15:15-17:45 | Rejected | Reason: "Overlapping with scheduled class" |


