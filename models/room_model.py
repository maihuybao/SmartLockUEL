from database import get_connection


def get_all_rooms():
    """Retrieve all rooms from the database.

    Returns:
        list[dict]: A list of dictionaries, each representing a room record
            with keys such as 'id', 'room_id', 'room_type', 'capacity', and 'status'.
    """
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rooms").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_rooms_by_status(status):
    """Retrieve rooms filtered by their status.

    Args:
        status (str): The room status to filter by (e.g., 'Available',
            'Occupied', or 'Full').

    Returns:
        list[dict]: A list of dictionaries for rooms matching the given status.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM rooms WHERE status = ?", (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_rooms(keyword):
    """Search for rooms by room ID or room type using a keyword.

    Args:
        keyword (str): The search term to match against room_id and room_type
            fields. Matching is case-insensitive and uses partial matching.

    Returns:
        list[dict]: A list of dictionaries for rooms whose room_id or room_type
            contains the keyword.
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM rooms WHERE room_id LIKE ? OR room_type LIKE ?",
        (f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_room(room_id, room_type, capacity, status="Available"):
    """Create a new room in the database.

    Args:
        room_id (str): The unique identifier for the room (e.g., 'A101').
        room_type (str): The type of room (e.g., 'Lecture Hall', 'Lab').
        capacity (int): The seating capacity of the room.
        status (str): The initial room status. Defaults to 'Available'.
            Must be one of 'Available', 'Occupied', or 'Full'.

    Returns:
        bool: True if the room was created successfully, False if the operation
            failed (e.g., duplicate room_id).
    """
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
    """Update an existing room record in the database.

    Args:
        pk (int): The primary key of the room to update.
        room_id (str): The new room identifier.
        room_type (str): The new room type.
        capacity (int): The new seating capacity.
        status (str): The new room status. Must be one of 'Available',
            'Occupied', or 'Full'.

    Returns:
        bool: True if the update succeeded, False if an error occurred
            (e.g., duplicate room_id).
    """
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
    """Delete a room from the database by primary key.

    Args:
        pk (int): The primary key of the room to delete.
    """
    conn = get_connection()
    conn.execute("DELETE FROM rooms WHERE id=?", (pk,))
    conn.commit()
    conn.close()
