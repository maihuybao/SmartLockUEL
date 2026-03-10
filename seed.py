"""Reset database and seed sample data."""

import os
import random
import string

DB_PATH = os.path.join(os.path.dirname(__file__), "datasets", "smartlocker.db")


def _generate_password(length=6):
    return "".join(random.choices(string.digits, k=length))


def seed():
    # Xoa DB cu, tao lai tu dau
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Removed old database.")

    from database import init_db, get_connection
    from models.user_model import hash_password

    init_db()
    conn = get_connection()

    # ── Users ────────────────────────────────────────────────────
    users = [
        ("admin", "admin123", "admin"),
        ("devadmin", "devadmin", "admin"),
        ("devuser", "devuser", "user"),
        ("sv001@st.uel.edu.vn", "123456", "user"),
        ("sv002@st.uel.edu.vn", "123456", "user"),
        ("sv003@st.uel.edu.vn", "123456", "user"),
        ("sv004@st.uel.edu.vn", "123456", "user"),
        ("sv005@st.uel.edu.vn", "123456", "user"),
        ("gv001@uel.edu.vn", "123456", "user"),
        ("gv002@uel.edu.vn", "123456", "user"),
    ]
    for username, password, role in users:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )

    # ── Rooms ────────────────────────────────────────────────────
    rooms = [
        ("A101", "Classroom", 50, "Available"),
        ("A102", "Classroom", 50, "Available"),
        ("A201", "Classroom", 100, "Available"),
        ("B101", "Meeting Room", 20, "Available"),
        ("B102", "Meeting Room", 20, "Occupied"),
        ("C101", "Study Room", 10, "Available"),
        ("C102", "Study Room", 10, "Available"),
        ("C103", "Study Room", 10, "Available"),
        ("D101", "Lab", 40, "Available"),
        ("D102", "Lab", 40, "Available"),
        ("E101", "Classroom", 50, "Available"),
        ("E102", "Classroom", 50, "Available"),
    ]
    for room_id, rtype, cap, status in rooms:
        conn.execute(
            "INSERT INTO rooms (room_id, room_type, capacity, status) VALUES (?, ?, ?, ?)",
            (room_id, rtype, cap, status),
        )

    # ── Devices ──────────────────────────────────────────────────
    # Lay room pk theo room_id
    def room_pk(rid):
        return conn.execute("SELECT id FROM rooms WHERE room_id=?", (rid,)).fetchone()[
            0
        ]

    devices = [
        (room_pk("A101"), "Smart Lock A101", _generate_password(), "Active"),
        (room_pk("A102"), "Smart Lock A102", _generate_password(), "Active"),
        (room_pk("A201"), "Smart Lock A201", _generate_password(), "Active"),
        (room_pk("B101"), "Smart Lock B101", _generate_password(), "Active"),
        (room_pk("B102"), "Smart Lock B102", _generate_password(), "Inactive"),
        (room_pk("C101"), "Smart Lock C101", _generate_password(), "Active"),
        (room_pk("C102"), "Smart Lock C102", _generate_password(), "Active"),
        (room_pk("C103"), "Smart Lock C103", None, "Maintenance"),
        (room_pk("D101"), "Smart Lock D101", _generate_password(), "Active"),
        (room_pk("D102"), "Smart Lock D102", _generate_password(), "Active"),
        (room_pk("E101"), "Smart Lock E101", _generate_password(), "Active"),
        (room_pk("E102"), "Smart Lock E102", _generate_password(), "Active"),
    ]
    for r_id, name, pw, status in devices:
        conn.execute(
            "INSERT INTO devices (room_id, device_name, cabinet_password, status) VALUES (?, ?, ?, ?)",
            (r_id, name, pw, status),
        )

    # ── Bookings ─────────────────────────────────────────────────
    def user_pk(uname):
        return conn.execute(
            "SELECT id FROM users WHERE username=?", (uname,)
        ).fetchone()[0]

    bookings = [
        # (user, room, session, reason, status, reject_reason, locker_password)
        (
            user_pk("sv001@st.uel.edu.vn"),
            room_pk("A101"),
            "2026-03-10 | 07:00 - 09:30",
            "Group study for final exam",
            "Approved",
            None,
            _generate_password(),
        ),
        (
            user_pk("sv002@st.uel.edu.vn"),
            room_pk("A101"),
            "2026-03-10 | 09:45 - 12:15",
            "Project presentation practice",
            "Approved",
            None,
            _generate_password(),
        ),
        (
            user_pk("sv003@st.uel.edu.vn"),
            room_pk("B101"),
            "2026-03-10 | 12:30 - 15:00",
            "Team meeting for capstone",
            "Pending",
            None,
            None,
        ),
        (
            user_pk("sv004@st.uel.edu.vn"),
            room_pk("C101"),
            "2026-03-10 | 15:15 - 17:45",
            "Self-study session",
            "Pending",
            None,
            None,
        ),
        (
            user_pk("sv005@st.uel.edu.vn"),
            room_pk("A102"),
            "2026-03-11 | 07:00 - 09:30",
            "Thesis discussion",
            "Rejected",
            "Room reserved for faculty use",
            None,
        ),
        (
            user_pk("gv001@uel.edu.vn"),
            room_pk("B101"),
            "2026-03-11 | 09:45 - 12:15",
            "Department meeting",
            "Approved",
            None,
            _generate_password(),
        ),
        (
            user_pk("sv001@st.uel.edu.vn"),
            room_pk("D101"),
            "2026-03-11 | 12:30 - 15:00",
            "Lab practice session",
            "Pending",
            None,
            None,
        ),
        (
            user_pk("sv002@st.uel.edu.vn"),
            room_pk("E101"),
            "2026-03-12 | 07:00 - 09:30",
            "Exam preparation",
            "Approved",
            None,
            _generate_password(),
        ),
        (
            user_pk("sv003@st.uel.edu.vn"),
            room_pk("C102"),
            "2026-03-12 | 09:45 - 12:15",
            "Research group meeting",
            "Pending",
            None,
            None,
        ),
        (
            user_pk("gv002@uel.edu.vn"),
            room_pk("A201"),
            "2026-03-12 | 15:15 - 17:45",
            "Lecture preparation",
            "Rejected",
            "Overlapping with scheduled class",
            None,
        ),
    ]
    for u_id, r_id, session, reason, status, reject_reason, locker_pw in bookings:
        conn.execute(
            """INSERT INTO bookings
               (user_id, room_id, session, reason, status, reject_reason, locker_password)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (u_id, r_id, session, reason, status, reject_reason, locker_pw),
        )

    conn.commit()
    conn.close()

    print("Database seeded successfully!")
    print(f"  Users   : {len(users)}")
    print(f"  Rooms   : {len(rooms)}")
    print(f"  Devices : {len(devices)}")
    print(f"  Bookings: {len(bookings)}")
    print("\nAdmin login: admin / admin123")
    print("User login : sv001@st.uel.edu.vn / 123456")


if __name__ == "__main__":
    seed()
