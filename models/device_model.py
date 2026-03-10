import random
import string
from database import get_connection


def get_all_devices():
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.*, r.room_id AS room_name
           FROM devices d JOIN rooms r ON d.room_id = r.id
           ORDER BY r.room_id, d.device_name"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_devices(keyword):
    kw = f"%{keyword}%"
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.*, r.room_id AS room_name
           FROM devices d JOIN rooms r ON d.room_id = r.id
           WHERE r.room_id LIKE ? OR d.device_name LIKE ? OR d.status LIKE ?
           ORDER BY r.room_id, d.device_name""",
        (kw, kw, kw),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_device(room_id, device_name, status="Active"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO devices (room_id, device_name, status) VALUES (?, ?, ?)",
            (room_id, device_name, status),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_device_password(device_id, new_password):
    conn = get_connection()
    conn.execute(
        "UPDATE devices SET cabinet_password=? WHERE id=?",
        (new_password, device_id),
    )
    conn.commit()
    conn.close()


def update_device_status(device_id, status):
    conn = get_connection()
    conn.execute(
        "UPDATE devices SET status=? WHERE id=?",
        (status, device_id),
    )
    conn.commit()
    conn.close()


def delete_device(device_id):
    conn = get_connection()
    conn.execute("DELETE FROM devices WHERE id=?", (device_id,))
    conn.commit()
    conn.close()


def generate_password():
    return "".join(random.choices(string.digits, k=6))
