from database import get_connection


def get_all_rooms():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_rooms_by_status(status):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM rooms WHERE status = ?", (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_rooms(keyword):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM rooms WHERE room_id LIKE ? OR room_type LIKE ?",
        (f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_room(room_id, room_type, capacity, status="Available"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO rooms (room_id, room_type, capacity, status) VALUES (?, ?, ?, ?)",
            (room_id, room_type, capacity, status),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_room(pk, room_id, room_type, capacity, status):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE rooms SET room_id=?, room_type=?, capacity=?, status=? WHERE id=?",
            (room_id, room_type, capacity, status, pk),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def delete_room(pk):
    conn = get_connection()
    conn.execute("DELETE FROM rooms WHERE id=?", (pk,))
    conn.commit()
    conn.close()
