# SmartLocker UEL — Technical Documentation

**Version:** 2.0
**Date:** 2026-03-10
**Platform:** Python 3.10+, PyQt6, SQLite 3

---

## 1. Project Overview

### 1.1 Purpose

SmartLocker UEL is a desktop application for managing room bookings and smart locker devices at the University of Economics and Law (UEL). It digitizes the room reservation process, enabling students and lecturers to book rooms online while administrators manage approvals, room inventory, users, and locker devices.

### 1.2 Scope

| Actor | Capabilities |
|---|---|
| Admin | View room grid, manage bookings (approve/reject), manage rooms (CRUD + CSV import), manage users (CRUD), manage devices (password management), export CSV |
| User | View available rooms with filters, submit booking requests, view booking history, edit/cancel pending bookings |

### 1.3 Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.10+ |
| GUI Framework | PyQt6 |
| UI Design | Qt Designer (.ui files), loaded via `PyQt6.uic.loadUi()` |
| Database | SQLite 3 — file at `datasets/smartlocker.db` |
| Password Hashing | SHA-256 via `hashlib` |
| Data Export | CSV via Python stdlib `csv` module |

### 1.4 Project Structure

```
SmartLockUEL/
├── main.py                    # Application entry point
├── database.py                # SQLite connection, schema init
├── seed.py                    # DB reset and sample data seeding
├── controllers/
│   ├── main_window.py         # Login screen
│   ├── overview_admin.py      # Admin home — room grid
│   ├── overview_users.py      # User home — room grid + booking
│   ├── booking_overview.py    # Admin — booking management
│   ├── edit_room.py           # Admin — room CRUD
│   ├── users_management.py    # Admin — user CRUD
│   └── device_management.py   # Admin — device management
├── models/
│   ├── user_model.py
│   ├── room_model.py
│   ├── booking_model.py
│   └── device_model.py
├── widgets/
│   ├── base_window.py         # Base class for all screens
│   ├── navbar.py              # Top navigation bar widget
│   ├── sidebar.py             # Left sidebar widget
│   └── room_card.py           # Room card widget
├── ui/                        # Qt Designer .ui files
│   ├── Login.ui
│   ├── MainWindow.ui
│   ├── OverviewAdmin.ui
│   ├── OverviewUsers.ui
│   ├── BookingDialog.ui
│   ├── BookingHistory.ui
│   ├── BookingOverview.ui
│   ├── RoomManagement.ui
│   ├── Users.ui
│   └── DeviceManagement.ui
└── datasets/
    └── smartlocker.db         # SQLite database file
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

Default credentials after seeding:

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| User | `sv001@st.uel.edu.vn` | `123456` |

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
        ├── [role = admin] ──► OverviewAdminController  (OverviewAdmin.ui)
        │                          ├── Sidebar: Bookings ──► BookingOverviewController
        │                          ├── Sidebar: Edit     ──► EditRoomController
        │                          ├── Sidebar: Users    ──► UsersManagementController
        │                          ├── Sidebar: Devices  ──► DeviceManagementController
        │                          └── Sidebar: Log Out  ──► MainWindowController
        │
        └── [role = user]  ──► OverviewUsersController  (OverviewUsers.ui)
                                   ├── Button: Booking  ──► BookingDialog  (QDialog)
                                   ├── NavBar: History  ──► BookingHistory (QDialog)
                                   └── Button: Log Out  ──► MainWindowController
```

Screen transitions follow this pattern:
```python
new_controller = TargetController(self.current_user)
self._transfer_window_state(new_controller)   # preserve size/position
new_controller.show()
self.close()
```

### 2.3 BaseWindow Layout

`BaseWindow` (`widgets/base_window.py`) is the base class for all controllers except `MainWindowController`. It builds the following layout automatically:

```
QMainWindow
  └── centralWidget (QWidget)
        └── QVBoxLayout
              ├── NavBar  (QFrame — top bar with search + role button)
              └── body    (QHBoxLayout)
                    ├── SideBar  (QFrame — left nav, optional)
                    └── QScrollArea
                          └── content_area  (QWidget)
                                └── QVBoxLayout
                                      └── [UI loaded by controller]
```

Controllers call `self.load_content_ui("FileName.ui")` to inject their screen into `content_area`. The `QScrollArea` wrapper ensures content is scrollable when the window is too small.

### 2.4 UI File — Controller Mapping

| .ui File | Controller | Notes |
|---|---|---|
| `Login.ui` | `controllers/main_window.py` | Standalone, no BaseWindow |
| `MainWindow.ui` | `widgets/base_window.py` | Shell layout |
| `OverviewAdmin.ui` | `controllers/overview_admin.py` | |
| `OverviewUsers.ui` | `controllers/overview_users.py` | |
| `BookingDialog.ui` | inline in `overview_users.py` | QDialog |
| `BookingHistory.ui` | inline in `overview_users.py` | QDialog |
| `BookingOverview.ui` | `controllers/booking_overview.py` | |
| `RoomManagement.ui` | `controllers/edit_room.py` | |
| `Users.ui` | `controllers/users_management.py` | |
| `DeviceManagement.ui` | `controllers/device_management.py` | |

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
│ role     │        │ session    │        │ capacity │
└──────────┘        │ reason     │        │ status   │
                    │ status     │        └──────┬───┘
                    │ reject_rsn │               │ 1
                    │ locker_pw  │               │
                    │ created_at │               │ N
                    └────────────┘        ┌──────┴───┐
                                          │ devices  │
                                          │──────────│
                                          │ id  (PK) │
                                          │ room_id  │
                                          │ dev_name │
                                          │ cab_pw   │
                                          │ status   │
                                          └──────────┘
```

### 3.2 Table: `users`

```sql
CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT    UNIQUE NOT NULL,
    password TEXT    NOT NULL,
    role     TEXT    NOT NULL CHECK(role IN ('admin', 'user'))
)
```

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `username` | TEXT | UNIQUE, NOT NULL | Login username (email format for users) |
| `password` | TEXT | NOT NULL | SHA-256 hex digest of the plain-text password |
| `role` | TEXT | CHECK IN ('admin','user') | Access level |

### 3.3 Table: `rooms`

```sql
CREATE TABLE rooms (
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

> **Note:** The `Full` status is computed **dynamically** at runtime in `widgets/room_card.py:_is_full_today()`. It is never written to the database. A room is considered Full when every 30-minute slot between 06:00 and 22:00 is covered by at least one active (Pending or Approved) booking for today.

### 3.4 Table: `bookings`

```sql
CREATE TABLE bookings (
    id              INTEGER   PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER   NOT NULL REFERENCES users(id),
    room_id         INTEGER   NOT NULL REFERENCES rooms(id),
    session         TEXT      NOT NULL,
    reason          TEXT      NOT NULL,
    status          TEXT      NOT NULL DEFAULT 'Pending'
                    CHECK(status IN ('Pending', 'Approved', 'Rejected')),
    reject_reason   TEXT,
    locker_password TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `user_id` | INTEGER | FK → users(id) | Booking owner |
| `room_id` | INTEGER | FK → rooms(id) | Target room |
| `session` | TEXT | NOT NULL | Time slot: `"YYYY-MM-DD \| HH:mm - HH:mm"` |
| `reason` | TEXT | NOT NULL | Purpose of booking |
| `status` | TEXT | CHECK, DEFAULT 'Pending' | Approval state |
| `reject_reason` | TEXT | NULL | Populated when status = Rejected |
| `locker_password` | TEXT | NULL | 6-digit code generated when Approved |
| `created_at` | TIMESTAMP | DEFAULT NOW | Record creation time |

### 3.5 Table: `devices`

```sql
CREATE TABLE devices (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id          INTEGER NOT NULL REFERENCES rooms(id),
    device_name      TEXT    NOT NULL,
    cabinet_password TEXT,
    status           TEXT    NOT NULL DEFAULT 'Active'
                     CHECK(status IN ('Active', 'Inactive', 'Maintenance'))
)
```

| Column | Type | Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | Primary key |
| `room_id` | INTEGER | FK → rooms(id) | Room this device belongs to |
| `device_name` | TEXT | NOT NULL | Device label (e.g. `Smart Lock A101`) |
| `cabinet_password` | TEXT | NULL | 6-digit locker PIN |
| `status` | TEXT | CHECK, DEFAULT 'Active' | Operational state |

---

## 4. Data Layer — Models

All model files contain **pure functions only** — no classes, no shared state. Each function opens a connection, executes a query, closes the connection, and returns a `dict` or `list[dict]`. Foreign key enforcement is enabled via `PRAGMA foreign_keys = ON`.

### 4.1 `models/user_model.py`

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `hash_password(password)` | `str` | `str` | Returns SHA-256 hex digest |
| `authenticate(username, password)` | `str, str` | `dict \| None` | Verifies credentials; returns user row or None |
| `get_all_users()` | — | `list[dict]` | All users (id, username, role) |
| `create_user(username, password, role)` | `str, str, str` | `bool` | Inserts new user; returns False on duplicate |
| `update_user(user_id, username, password, role)` | `int, str, str, str` | `bool` | Updates user; empty password = keep existing hash |
| `delete_user(user_id)` | `int` | — | Deletes user by id |

### 4.2 `models/room_model.py`

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `get_all_rooms()` | — | `list[dict]` | All rooms |
| `get_rooms_by_status(status)` | `str` | `list[dict]` | Filter by status value |
| `search_rooms(keyword)` | `str` | `list[dict]` | LIKE search on room_id and room_type |
| `create_room(room_id, room_type, capacity, status)` | `str, str, int, str` | `bool` | Insert new room |
| `update_room(pk, room_id, room_type, capacity, status)` | `int, str, str, int, str` | `bool` | Update room by primary key |
| `delete_room(pk)` | `int` | — | Delete room by primary key |

### 4.3 `models/booking_model.py`

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `get_bookings_by_user(user_id)` | `int` | `list[dict]` | All bookings for a user (JOIN rooms) |
| `get_all_bookings()` | — | `list[dict]` | All bookings (JOIN rooms + users) |
| `create_booking(user_id, room_id, session, reason)` | `int, int, str, str` | `bool` | Create booking with status=Pending |
| `update_booking(booking_id, session, reason)` | `int, str, str` | — | Update time/reason (Pending only) |
| `cancel_booking(booking_id)` | `int` | — | Delete booking (Pending only) |
| `approve_booking(booking_id)` | `int` | `str` | Set Approved, generate 6-digit locker_password, return it |
| `reject_booking(booking_id, reason)` | `int, str` | — | Set Rejected, store reject_reason |
| `delete_booking(booking_id)` | `int` | — | Hard delete (Admin, any status) |
| `admin_update_booking(booking_id, session, reason, status)` | `int, str, str, str` | — | Admin full update |
| `get_dashboard_stats()` | — | `dict` | Counts: total_rooms, total_bookings, pending, approved, rejected |
| `get_bookings_by_room(room_pk)` | `int` | `list[dict]` | Active bookings (Pending/Approved) for a room |
| `get_bookings_by_room_date(room_pk, date_str)` | `int, str` | `list[dict]` | Active bookings for a room on a specific date |
| `has_conflict(room_pk, date_str, start_str, end_str, exclude_id)` | `int, str, str, str, int\|None` | `bool` | Check time overlap; exclude_id skips one booking (for edit) |

**Conflict detection algorithm:**

Two time intervals `[ns, ne)` and `[bs, be)` overlap when:
```
ns < be  AND  ne > bs
```
This is the standard interval overlap test. The function converts `"HH:mm"` strings to minutes-since-midnight before comparing.

### 4.4 `models/device_model.py`

| Function | Parameters | Returns | Description |
|---|---|---|---|
| `get_all_devices()` | — | `list[dict]` | All devices (JOIN rooms for room_id text) |
| `search_devices(keyword)` | `str` | `list[dict]` | LIKE search on room_id, device_name, status |
| `create_device(room_id, device_name, status)` | `int, str, str` | `bool` | Insert new device |
| `update_device_password(device_id, new_password)` | `int, str` | — | Update cabinet_password |
| `update_device_status(device_id, status)` | `int, str` | — | Update device status |
| `delete_device(device_id)` | `int` | — | Delete device |
| `generate_password()` | — | `str` | Return random 6-digit string |

---

## 5. Controllers

### 5.1 `MainWindowController` (`controllers/main_window.py`)

Inherits `QMainWindow` directly (not `BaseWindow`). Loads `Login.ui`.

**Login flow:**
1. User enters username + password, selects role radio button (Admin / User)
2. `authenticate(username, password)` hashes the input with SHA-256 and compares against DB
3. If credentials match but role does not match the radio button → error
4. On success → instantiate `OverviewAdminController` or `OverviewUsersController`, show it, close login

**Additional features:**
- Background image rendered scale-to-cover via `paintEvent` mixin (`_BgWidget`)
- Toggle password visibility (eye icon button)
- F11 shortcut for fullscreen toggle

### 5.2 `OverviewAdminController` (`controllers/overview_admin.py`)

Inherits `BaseWindow`. Loads `OverviewAdmin.ui`.

**Features:**
- Responsive room card grid (recalculates columns on `resizeEvent` and `showEvent`)
- Status filter buttons: All / Available / Occupied / Full
- Real-time search via navbar `lineEditSearch`
- Right-click context menu on any card → "Edit Room" → navigates to `EditRoomController` with `preselect_room`

**Grid column calculation:**
```python
cols = max(1, available_width // (card_width + spacing))
```

### 5.3 `OverviewUsersController` (`controllers/overview_users.py`)

Inherits `BaseWindow`. Loads `OverviewUsers.ui`.

**Three independent filter groups:**

| Group | Options |
|---|---|
| Status | All / Available / Occupied / Full |
| Capacity | All / ≤50 seats / 100+ seats |
| Session | All / Morning (06–12) / Afternoon (12–17) / Evening (17–22) |

Session filter calls `_has_free_slot(room_pk, date_str, range_start, range_end)` — returns True if any 30-minute slot in the range is not covered by an active booking today.

**Booking Dialog (`BookingDialog.ui`):**
- Room combo, date picker, start/end time (constrained to 06:00–22:00)
- Availability table: 16 columns (hours 06–21), color-coded per hour slot:
  - Green (`#A5D6A7`) = free
  - Amber (`#FFE082`) = Pending booking
  - Red (`#EF9A9A`) = Approved booking
- Conflict check via `has_conflict()` before submitting
- Session string stored as: `"YYYY-MM-DD | HH:mm - HH:mm"`

**Booking History (`BookingHistory.ui`):**
- Filter by status (All / Pending / Approved / Rejected)
- Pending rows show Edit + Cancel buttons inline
- Approved rows show `locker_password`
- Rejected rows show `reject_reason` in red

### 5.4 `BookingOverviewController` (`controllers/booking_overview.py`)

Inherits `BaseWindow`. Loads `BookingOverview.ui`.

**Features:**
- Full booking table with columns: User, Room, Type, Date, Start, End, Purpose, Status, Password, Edit, Delete
- Filter by status + keyword search (username, room name, session)
- **Approve**: calls `approve_booking()` → auto-generates 6-digit `locker_password`, shows it in a dialog
- **Reject**: prompts for reason → calls `reject_booking(id, reason)`
- **Add**: Admin creates a booking on behalf of any user
- **Edit / Delete**: inline buttons per row
- **Export CSV**: exports current filtered view to a user-selected file path

### 5.5 `EditRoomController` (`controllers/edit_room.py`)

Inherits `BaseWindow`. Loads `RoomManagement.ui`.

**Features:**
- Room table with real-time search
- Form fields: Room ID, Room Type, Capacity, Status (`QComboBox`: Available / Occupied)
- CRUD: Create / Update / Delete
- **Import CSV**: reads `room_id, room_type, capacity, status` columns; reports imported/skipped counts
- Supports `preselect_room` parameter to highlight a specific room on load (called from Admin Overview right-click)

### 5.6 `UsersManagementController` (`controllers/users_management.py`)

Inherits `BaseWindow`. Loads `Users.ui`.

**Features:**
- User table with search by username/role
- Form: Username, Password, Role (`QComboBox`: admin / user)
- CRUD: Create / Update / Delete
- Guard: cannot delete the currently logged-in user
- Password displayed as `••••••` in the table

### 5.7 `DeviceManagementController` (`controllers/device_management.py`)

Inherits `BaseWindow`. Loads `DeviceManagement.ui`.

**Features:**
- Device table (JOIN rooms) with keyword search
- Add device: select room from combo, enter name, select status
- Select a device row → Generate new 6-digit password → Confirm to save
- Delete device

---

## 6. Widgets

### 6.1 `BaseWindow` (`widgets/base_window.py`)

| Method | Description |
|---|---|
| `__init__(user, role_text, show_search, show_sidebar, title)` | Builds NavBar + optional SideBar + ScrollArea layout |
| `load_content_ui(filename)` | Loads `ui/<filename>` into `content_area`, returns the widget |
| `_connect_sidebar()` | Override to wire sidebar button signals |
| `_go_overview/bookings/edit/users/devices()` | Navigate to the corresponding controller |
| `_transfer_window_state(target)` | Copy current window geometry to target before showing |
| `_toggle_fullscreen()` | F11 handler |
| `_logout()` | Confirm dialog → return to `MainWindowController` |
| `_quit()` | Confirm dialog → `QApplication.quit()` |

### 6.2 `NavBar` (`widgets/navbar.py`)

Loaded from `navbar.ui`. Contains:
- Application title/logo
- `btnRole`: shows current role; for Users, clicking opens Booking History
- `lineEditSearch`: real-time search input (hidden when `show_search=False`)

### 6.3 `SideBar` (`widgets/sidebar.py`)

Loaded from `sidebar.ui`. Navigation buttons: Overview, Bookings, Edit, Users, Devices, Log Out, Quit.

### 6.4 `room_card` (`widgets/room_card.py`)

Creates a `QWidget` card (200 × 110 px) for each room.

**Status color scheme:**

| Status | Border / Badge | Background |
|---|---|---|
| Available | `#4CAF50` (green) | `#E8F5E9` |
| Occupied | `#F44336` (red) | `#FFEBEE` |
| Full | `#FF9800` (orange) | `#FFF3E0` |

**`get_display_status(room)`** — returns the visual status:
```python
def get_display_status(room):
    if room["status"] == "Available" and _is_full_today(room["id"]):
        return "Full"
    return room["status"]
```

**`_is_full_today(room_pk)`** — dynamic Full detection:
1. Fetch all Pending/Approved bookings for the room today
2. Build a set of occupied 30-minute slots (in minutes since midnight)
3. If every slot in `range(360, 1320, 30)` (06:00–22:00) is in the set → return `True`

---

## 7. Key Algorithms & Business Logic

### 7.1 Booking Conflict Detection

```python
def has_conflict(room_pk, date_str, start_str, end_str, exclude_id=None):
    bookings = get_bookings_by_room_date(room_pk, date_str)
    ns = _to_minutes(start_str)   # new start
    ne = _to_minutes(end_str)     # new end
    for b in bookings:
        if exclude_id and b["id"] == exclude_id:
            continue              # skip self when editing
        bs, be = parse booking times
        if ns < be and ne > bs:   # standard interval overlap
            return True
    return False
```

The `exclude_id` parameter allows editing an existing booking without it conflicting with itself.

### 7.2 Dynamic "Full" Status

```python
def _is_full_today(room_pk):
    today = date.today().strftime("%Y-%m-%d")
    bookings = get_bookings_by_room_date(room_pk, today)
    occupied = set()
    for b in bookings:
        for slot in range(start_min, end_min, 30):
            occupied.add(slot)
    all_slots = set(range(6 * 60, 22 * 60, 30))   # 06:00–22:00
    return all_slots.issubset(occupied)
```

### 7.3 Responsive Grid Layout

```python
card_w  = 200
spacing = layout.horizontalSpacing() or 10
cols    = max(1, (content_area.width() - 20) // (card_w + spacing))
```

Recalculated in both `resizeEvent` and `showEvent` to adapt to any window size.

### 7.4 Locker Password Generation

```python
import random, string

def _generate_locker_password():
    return "".join(random.choices(string.digits, k=6))
```

Called automatically when an admin approves a booking. The 6-digit code is stored in `bookings.locker_password` and displayed to the user in Booking History.

### 7.5 Session Time Filter (`_has_free_slot`)

```python
TIME_RANGES = {
    "Morning":   (6 * 60,  12 * 60),
    "Afternoon": (12 * 60, 17 * 60),
    "Evening":   (17 * 60, 22 * 60),
}

def _has_free_slot(room_pk, date_str, range_start, range_end):
    bookings = get_bookings_by_room_date(room_pk, date_str)
    booked = set()
    for b in bookings:
        for slot in range(start_min, end_min, 30):
            booked.add(slot)
    return any(slot not in booked for slot in range(range_start, range_end, 30))
```

A room passes the session filter if it has **at least one free 30-minute slot** within the selected time range today.

### 7.6 Availability Table Rendering

The `BookingDialog` shows a 16-column table (one column per hour, 06–21). For each hour slot:

```
slot_s = hour * 60
slot_e = (hour + 1) * 60

For each active booking [bs, be, status]:
    if bs < slot_e and be > slot_s:   → slot is occupied
        if status == "Approved" → color RED
        else                    → color AMBER
    else                        → color GREEN
```

---

## 8. Sample Data

Running `python3 seed.py` deletes the existing database and recreates it with the following data:

### 8.1 Users (8 total)

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | admin |
| `sv001@st.uel.edu.vn` | `123456` | user |
| `sv002@st.uel.edu.vn` | `123456` | user |
| `sv003@st.uel.edu.vn` | `123456` | user |
| `sv004@st.uel.edu.vn` | `123456` | user |
| `sv005@st.uel.edu.vn` | `123456` | user |
| `gv001@uel.edu.vn` | `123456` | user |
| `gv002@uel.edu.vn` | `123456` | user |

### 8.2 Rooms (12 total)

| Room ID | Type | Capacity | Status |
|---|---|---|---|
| A101 | Classroom | 50 | Available |
| A102 | Classroom | 50 | Available |
| A201 | Classroom | 100 | Available |
| B101 | Meeting Room | 20 | Available |
| B102 | Meeting Room | 20 | Occupied |
| C101–C103 | Study Room | 10 | Available |
| D101–D102 | Lab | 40 | Available |
| E101–E102 | Classroom | 50 | Available |

### 8.3 Devices (12 total)

One Smart Lock device per room. Device C103 has no password (Maintenance status). Device B102 is Inactive.

### 8.4 Bookings (10 total)

| User | Room | Date | Time | Status |
|---|---|---|---|---|
| sv001 | A101 | 2026-03-10 | 07:00–09:30 | Approved |
| sv002 | A101 | 2026-03-10 | 09:45–12:15 | Approved |
| sv003 | B101 | 2026-03-10 | 12:30–15:00 | Pending |
| sv004 | C101 | 2026-03-10 | 15:15–17:45 | Pending |
| sv005 | A102 | 2026-03-11 | 07:00–09:30 | Rejected |
| gv001 | B101 | 2026-03-11 | 09:45–12:15 | Approved |
| sv001 | D101 | 2026-03-11 | 12:30–15:00 | Pending |
| sv002 | E101 | 2026-03-12 | 07:00–09:30 | Approved |
| sv003 | C102 | 2026-03-12 | 09:45–12:15 | Pending |
| gv002 | A201 | 2026-03-12 | 15:15–17:45 | Rejected |
