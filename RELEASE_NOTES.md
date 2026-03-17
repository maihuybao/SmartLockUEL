# Release Notes - SmartLocker UEL

## v1.1.0 — Multilingual Support

### New Features

- **English/Vietnamese language switching**: Full UI support for both languages with real-time switching.
  - Language toggle button (EN/VI) on the navbar and login screen.
  - Language preference persists between sessions.
  - All labels, buttons, messages, tooltips, table headers, and dialog titles are translated.

### Technical Changes

- Added `i18n.py` — translation module with `tr()` function and `LanguageManager` singleton.
- Added `datasets/language.json` — 189 translation keys per language.
- Added `btnLang` button to `ui/navbar.ui`.
- All controllers and widgets use `tr()` instead of hardcoded strings.
- Language preference saved to `datasets/lang_pref.txt`.

### Build

- Updated `build.command`: macOS output to `dist/macOS`, Windows output to `dist/Windows`.
- Bundled `datasets/language.json` into the executable.

---

## v1.0.0 — Initial Release

### Core Features

**Admin (5 tabs)**
- Dashboard with statistics and responsive room card grid.
- Booking management: approve/reject with auto-generated 6-digit locker password, import/export CSV.
- Room management: CRUD, status filtering, import/export CSV.
- User management: CRUD, role filtering, view booking history per user, import/export CSV.
- Device management: CRUD, status filtering, password generation/reset, import/export CSV.

**User (Student / Lecturer)**
- Room grid with 3 independent filter groups: status, capacity, session (Morning/Afternoon/Evening).
- Availability table with 30-minute slots (06:00–22:00).
- Room booking with automatic time conflict detection.
- Booking history with edit/cancel for Pending bookings.
- Locker password displayed when booking is Approved.

### Architecture

- Python 3.10+ / PyQt6 / SQLite.
- UI designed with Qt Designer (18 `.ui` files).
- Admin uses `QStackedWidget` (5 pages in a single window).
- User uses `QScrollArea` (single-page layout).
- Passwords stored as SHA-256 hash, Full status computed dynamically at runtime.
