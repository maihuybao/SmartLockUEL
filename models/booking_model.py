import random
import string
from database import get_connection


def get_bookings_by_user(user_id):
    conn = get_connection()
    rows = conn.execute(
        """SELECT b.*, r.room_id AS room_name, r.room_type
           FROM bookings b JOIN rooms r ON b.room_id = r.id
           WHERE b.user_id = ? ORDER BY b.created_at DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_bookings():
    conn = get_connection()
    rows = conn.execute(
        """SELECT b.*, r.room_id AS room_name, r.room_type,
                  u.username
           FROM bookings b
           JOIN rooms r ON b.room_id = r.id
           JOIN users u ON b.user_id = u.id
           ORDER BY b.created_at DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_booking(user_id, room_id, session, reason):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO bookings (user_id, room_id, session, reason) VALUES (?, ?, ?, ?)",
            (user_id, room_id, session, reason),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_booking(booking_id, session, reason):
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET session=?, reason=? WHERE id=? AND status='Pending'",
        (session, reason, booking_id),
    )
    conn.commit()
    conn.close()


def cancel_booking(booking_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM bookings WHERE id=? AND status='Pending'",
        (booking_id,),
    )
    conn.commit()
    conn.close()


def _generate_locker_password():
    return "".join(random.choices(string.digits, k=6))


def approve_booking(booking_id):
    conn = get_connection()
    password = _generate_locker_password()
    conn.execute(
        "UPDATE bookings SET status='Approved', locker_password=? WHERE id=?",
        (password, booking_id),
    )
    conn.commit()
    conn.close()
    return password


def reject_booking(booking_id, reason):
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET status='Rejected', reject_reason=? WHERE id=?",
        (reason, booking_id),
    )
    conn.commit()
    conn.close()


def get_dashboard_stats():
    conn = get_connection()
    total_rooms = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    pending = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE status='Pending'"
    ).fetchone()[0]
    approved = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE status='Approved'"
    ).fetchone()[0]
    rejected = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE status='Rejected'"
    ).fetchone()[0]
    conn.close()
    return {
        "total_rooms": total_rooms,
        "total_bookings": total_bookings,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
    }


def delete_booking(booking_id):
    conn = get_connection()
    conn.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()


def admin_update_booking(booking_id, session, reason, status):
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET session=?, reason=?, status=? WHERE id=?",
        (session, reason, status, booking_id),
    )
    conn.commit()
    conn.close()


def get_all_users_simple():
    conn = get_connection()
    rows = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_bookings_by_room(room_pk):
    """Get active bookings (Pending/Approved) for a specific room."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT session, status FROM bookings
           WHERE room_id = ? AND status IN ('Pending', 'Approved')""",
        (room_pk,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_bookings_by_room_date(room_pk, date_str):
    """Get active bookings for a room on a specific date (YYYY-MM-DD)."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, session, status FROM bookings
           WHERE room_id = ? AND status IN ('Pending', 'Approved')
           AND session LIKE ?""",
        (room_pk, f"{date_str} |%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _to_minutes(t):
    h, m = map(int, t.strip().split(":"))
    return h * 60 + m


def has_conflict(room_pk, date_str, start_str, end_str, exclude_id=None):
    """Return True if the slot overlaps any existing Pending/Approved booking."""
    bookings = get_bookings_by_room_date(room_pk, date_str)
    ns, ne = _to_minutes(start_str), _to_minutes(end_str)
    for b in bookings:
        if exclude_id is not None and b["id"] == exclude_id:
            continue
        if " | " not in b["session"]:
            continue
        _, tp = b["session"].split(" | ", 1)
        if " - " not in tp:
            continue
        bs_str, be_str = tp.split(" - ", 1)
        bs, be = _to_minutes(bs_str), _to_minutes(be_str)
        if ns < be and ne > bs:
            return True
    return False
