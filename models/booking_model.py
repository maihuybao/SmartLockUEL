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
