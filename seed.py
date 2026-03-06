"""Seed initial data: admin account + sample rooms."""
from database import init_db, get_connection
from models.user_model import hash_password


def seed():
    init_db()
    conn = get_connection()

    # Admin account
    existing = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "admin"),
        )

    # Sample user
    existing = conn.execute("SELECT id FROM users WHERE username='sv001@st.uel.edu.vn'").fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("sv001@st.uel.edu.vn", hash_password("123456"), "user"),
        )

    # Sample rooms
    sample_rooms = [
        ("A101", "Phong hoc", 50, "Available"),
        ("A102", "Phong hoc", 50, "Available"),
        ("A201", "Phong hoc", 100, "Available"),
        ("B101", "Phong hoi thao", 100, "Available"),
        ("B102", "Phong hoi thao", 50, "Occupied"),
        ("C101", "Phong tu hoc", 50, "Available"),
        ("C102", "Phong tu hoc", 50, "Cleaning"),
    ]
    for room_id, rtype, cap, status in sample_rooms:
        existing = conn.execute(
            "SELECT id FROM rooms WHERE room_id=?", (room_id,)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO rooms (room_id, room_type, capacity, status) VALUES (?, ?, ?, ?)",
                (room_id, rtype, cap, status),
            )

    conn.commit()
    conn.close()
    print("Seed data created successfully!")


if __name__ == "__main__":
    seed()
