import random
import string
from database import get_connection


def get_bookings_by_user(user_id):
    """Retrieve all bookings for a specific user, ordered by creation date descending.

    Args:
        user_id (int): The primary key of the user whose bookings to retrieve.

    Returns:
        list[dict]: A list of dictionaries, each representing a booking record
            with additional 'room_name' and 'room_type' fields from the joined
            rooms table.
    """
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
    """Retrieve all bookings with associated user and room information.

    Returns:
        list[dict]: A list of dictionaries, each representing a booking record
            with additional 'room_name', 'room_type', and 'username' fields,
            ordered by creation date descending.
    """
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


def create_booking(user_id, room_id, date, time_start, time_end, reason):
    """Create a new booking in the database with a default 'Pending' status.

    Args:
        user_id (int): The primary key of the user making the booking.
        room_id (int): The primary key of the room being booked.
        date (str): The booking date in 'YYYY-MM-DD' format.
        time_start (str): The start time in 'HH:mm' format.
        time_end (str): The end time in 'HH:mm' format.
        reason (str): The purpose or reason for the booking.

    Returns:
        bool: True if the booking was created successfully, False if the
            operation failed.
    """
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO bookings (user_id, room_id, date, time_start, time_end, reason) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, room_id, date, time_start, time_end, reason),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_booking(booking_id, date, time_start, time_end, reason):
    """Update a booking that is still in 'Pending' status.

    Only bookings with status 'Pending' can be updated through this function.

    Args:
        booking_id (int): The primary key of the booking to update.
        date (str): The new booking date in 'YYYY-MM-DD' format.
        time_start (str): The new start time in 'HH:mm' format.
        time_end (str): The new end time in 'HH:mm' format.
        reason (str): The new purpose or reason for the booking.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET date=?, time_start=?, time_end=?, reason=? WHERE id=? AND status='Pending'",
        (date, time_start, time_end, reason, booking_id),
    )
    conn.commit()
    conn.close()


def cancel_booking(booking_id):
    """Cancel a booking by deleting it, only if its status is 'Pending'.

    Args:
        booking_id (int): The primary key of the booking to cancel.
    """
    conn = get_connection()
    conn.execute(
        "DELETE FROM bookings WHERE id=? AND status='Pending'",
        (booking_id,),
    )
    conn.commit()
    conn.close()


def _generate_locker_password():
    """Generate a random 6-digit numeric locker password.

    Returns:
        str: A string of 6 random digits (e.g., '583012').
    """
    return "".join(random.choices(string.digits, k=6))


def approve_booking(booking_id):
    """Approve a booking and assign a generated locker password.

    Sets the booking status to 'Approved' and generates a 6-digit locker
    password that the user can use to access the room cabinet.

    Args:
        booking_id (int): The primary key of the booking to approve.

    Returns:
        str: The generated 6-digit locker password assigned to the booking.
    """
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
    """Reject a booking and record the rejection reason.

    Sets the booking status to 'Rejected' and stores the reason provided
    by the administrator.

    Args:
        booking_id (int): The primary key of the booking to reject.
        reason (str): The reason for rejecting the booking.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET status='Rejected', reject_reason=? WHERE id=?",
        (reason, booking_id),
    )
    conn.commit()
    conn.close()


def get_dashboard_stats():
    """Retrieve summary statistics for the admin dashboard.

    Returns:
        dict: A dictionary with the following keys:
            - 'total_rooms' (int): Total number of rooms.
            - 'total_bookings' (int): Total number of bookings.
            - 'pending' (int): Number of bookings with 'Pending' status.
            - 'approved' (int): Number of bookings with 'Approved' status.
            - 'rejected' (int): Number of bookings with 'Rejected' status.
    """
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
    """Delete a booking from the database by primary key.

    Args:
        booking_id (int): The primary key of the booking to delete.
    """
    conn = get_connection()
    conn.execute("DELETE FROM bookings WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()


def admin_update_booking(booking_id, date, time_start, time_end, reason, status):
    """Update any booking regardless of its current status (admin-only operation).

    Unlike ``update_booking``, this function allows changing the status field
    and does not restrict updates to 'Pending' bookings only.

    Args:
        booking_id (int): The primary key of the booking to update.
        date (str): The new booking date in 'YYYY-MM-DD' format.
        time_start (str): The new start time in 'HH:mm' format.
        time_end (str): The new end time in 'HH:mm' format.
        reason (str): The new purpose or reason for the booking.
        status (str): The new booking status. Must be one of 'Pending',
            'Approved', or 'Rejected'.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE bookings SET date=?, time_start=?, time_end=?, reason=?, status=? WHERE id=?",
        (date, time_start, time_end, reason, status, booking_id),
    )
    conn.commit()
    conn.close()


def get_all_users_simple():
    """Retrieve a minimal list of all users, ordered by username.

    Returns:
        list[dict]: A list of dictionaries, each containing 'id' and 'username'
            keys for a user.
    """
    conn = get_connection()
    rows = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_bookings_by_room(room_pk):
    """Retrieve active bookings (Pending or Approved) for a specific room.

    Args:
        room_pk (int): The primary key of the room to query.

    Returns:
        list[dict]: A list of dictionaries, each containing 'date',
            'time_start', 'time_end', and 'status' for an active booking.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT date, time_start, time_end, status FROM bookings
           WHERE room_id = ? AND status IN ('Pending', 'Approved')""",
        (room_pk,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_bookings_by_room_date(room_pk, date_str):
    """Retrieve active bookings for a room on a specific date.

    Args:
        room_pk (int): The primary key of the room to query.
        date_str (str): The date to filter by in 'YYYY-MM-DD' format.

    Returns:
        list[dict]: A list of dictionaries, each containing 'id', 'date',
            'time_start', 'time_end', and 'status' for active bookings on
            the specified date.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, date, time_start, time_end, status FROM bookings
           WHERE room_id = ? AND status IN ('Pending', 'Approved')
           AND date = ?""",
        (room_pk, date_str),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _to_minutes(t):
    """Convert a time string in 'HH:mm' format to total minutes since midnight.

    Args:
        t (str): A time string in 'HH:mm' format (e.g., '14:30').

    Returns:
        int: The number of minutes since midnight (e.g., 870 for '14:30').

    Raises:
        ValueError: If the time string is not in valid 'HH:mm' format.
    """
    h, m = map(int, t.strip().split(":"))
    return h * 60 + m


def has_conflict(room_pk, date_str, start_str, end_str, exclude_id=None):
    """Check whether a proposed time slot overlaps any existing active booking.

    Compares the proposed slot against all Pending and Approved bookings
    for the same room and date. An optional booking ID can be excluded to
    allow updates to an existing booking without self-conflict.

    Args:
        room_pk (int): The primary key of the room to check.
        date_str (str): The date of the proposed booking in 'YYYY-MM-DD' format.
        start_str (str): The proposed start time in 'HH:mm' format.
        end_str (str): The proposed end time in 'HH:mm' format.
        exclude_id (int or None): An optional booking ID to exclude from the
            conflict check. Defaults to None.

    Returns:
        bool: True if the proposed slot overlaps an existing booking,
            False otherwise.
    """
    bookings = get_bookings_by_room_date(room_pk, date_str)
    ns, ne = _to_minutes(start_str), _to_minutes(end_str)
    for b in bookings:
        if exclude_id is not None and b["id"] == exclude_id:
            continue
        bs, be = _to_minutes(b["time_start"]), _to_minutes(b["time_end"])
        if ns < be and ne > bs:
            return True
    return False
