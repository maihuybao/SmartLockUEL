Design an implementation plan for adding English/Vietnamese language switching to a PyQt6 desktop application (SmartLocker UEL).

## Requirements
1. Create `datasets/language.json` with translations for all UI text (English and Vietnamese)
2. Create a language toggle button next to the role badge in the navbar
3. All UI text (both from .ui files and hardcoded Python strings) must be translatable
4. Language preference should persist (saved to a file or the JSON itself)

## Current Architecture
- PyQt6 app with `BaseWindow` base class in `widgets/base_window.py`
- `NavBar` widget in `widgets/navbar.py` loads `ui/navbar.ui`, has `btnRole` for role badge
- `SideBar` widget in `widgets/sidebar.py` loads `ui/sidebar.ui`
- Controllers inherit `BaseWindow` which has `self.navbar` accessible
- Admin uses `AdminShellController` (stack mode with 5 pages), User uses `OverviewUsersController` (scroll mode)
- Login screen is `MainWindowController` in `controllers/main_window.py` which loads `Login.ui` directly (does NOT inherit BaseWindow)
- All .ui files loaded via `uic.loadUi(path, widget)`
- `paths.py` has `resource_dir()` and `data_dir()` for PyInstaller support

## Key Design Decisions Needed

### Approach for translation system
Option A: Create a central `i18n.py` module with a `tr(key)` function. Store current language as module-level state. Each controller calls `tr("key")` for strings and has a `retranslate_ui()` method to update .ui widget texts.

Option B: Use Qt's built-in QTranslator system with .ts/.qm files.

I recommend Option A because:
- The project uses `uic.loadUi()` which makes Qt's lupdate tool harder to use
- A simple JSON + tr() approach is more transparent and easier to maintain
- The project is small enough that a custom solution is cleaner

### How to handle .ui file texts
After `uic.loadUi()` loads a .ui file, we override the widget texts in Python using `retranslate_ui()` methods. This means:
- .ui files keep their English text as defaults
- Each controller implements `retranslate_ui()` to set all widget texts from translations
- `retranslate_ui()` is called after init and whenever language changes

### How language switching works at runtime
When user clicks the language toggle:
1. `i18n.py` updates current language
2. Signal emitted to all open windows
3. Each window calls its `retranslate_ui()` to update all visible text

### Signal propagation
Use a singleton pattern or module-level signal. Since PyQt6 requires QObject for signals, create a small `LanguageManager` QObject singleton that emits `language_changed` signal.

## Files to Create
1. `datasets/language.json` - all translations
2. `i18n.py` - translation module with `tr()`, `LanguageManager`, language persistence

## Files to Modify
1. `ui/navbar.ui` - add language toggle button next to btnRole
2. `widgets/navbar.py` - connect language button, toggle logic
3. `widgets/base_window.py` - connect to language_changed signal, call retranslate_ui()
4. `widgets/sidebar.py` - add retranslate_ui()
5. `widgets/room_card.py` - use tr() for card text
6. `controllers/main_window.py` - add retranslate_ui() for login screen (special case: no BaseWindow)
7. `controllers/admin_shell.py` - connect language signal
8. `controllers/overview_admin.py` - add retranslate_ui()
9. `controllers/overview_users.py` - add retranslate_ui() and use tr() for QMessageBox strings
10. `controllers/booking_overview.py` - add retranslate_ui() and use tr()
11. `controllers/edit_room.py` - add retranslate_ui() and use tr()
12. `controllers/users_management.py` - add retranslate_ui() and use tr()
13. `controllers/device_management.py` - add retranslate_ui() and use tr()

## Complete list of translatable strings (grouped by context)

### Navbar
- "SmartLocker UEL", "Search...", "Admin", "User", "EN", "VI"

### Sidebar
- "Dashboard", "Booking Management", "Room Management", "Users Management", "Devices Management", "Log out", "Quit"

### Login
- "SmartLocker UEL", "University of Economics and Law...", "Email:", "Password:", "Enter password", "Lecturer/Student", "Administrator", "Login"

### Common
- "Error", "Success", "Confirm", "Cancel", "Save", "Close", "Delete", "Edit", "View"
- "Are you sure you want to log out?", "Are you sure you want to quit?"
- "Log out", "Quit"

### Room statuses
- "Available", "Occupied", "Full", "All"

### Booking statuses  
- "Pending", "Approved", "Rejected", "All Status"

### Overview Admin
- "Total Rooms", "Total Bookings", "Pending", "Approved", "Rejected"
- "Edit Room" (context menu)

### Overview Users
- "Capacity:", "Session:", "≤ 50", "100+"
- "Morning (06-12)", "Afternoon (12-17)", "Evening (17-22)"
- "My Bookings", "Booking", "Book Room"
- Various QMessageBox messages for booking flow

### Booking Management
- "Booking Management", "+ Add", "Import CSV", "Export CSV"
- Table headers: "Full Name", "Room", "Room Type", "Date", "Start Time", "End Time", "Purpose", "Status", "Password", "Actions"
- QMessageBox messages for approve/reject/delete/import/export

### Room Management
- "Room Management", table headers, QMessageBox messages

### Users Management
- "Users Management", table headers, QMessageBox messages

### Device Management
- "Device Management", table headers, QMessageBox messages

### Dialogs
- BookingDialog, AdminBookingDialog, BookingDetails, BookingHistory, RoomDialog, UserDialog, DeviceDialog - all their labels, placeholders, buttons

### Room Card
- "{n} active booking(s)", "No active bookings", "{type} · {capacity} seats"

Please design a detailed, step-by-step implementation plan considering all of the above. Focus on making the plan practical and minimizing the risk of breaking existing functionality.