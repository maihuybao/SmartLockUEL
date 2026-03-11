import random
import string
from database import get_connection


def get_all_devices():
    """Retrieve all devices from the database with their associated room names.

    Devices are returned sorted by room ID and then by device name.

    Returns:
        list[dict]: A list of dictionaries, each representing a device record
            with keys including 'id', 'room_id', 'device_name',
            'cabinet_password', 'status', and 'room_name'.
    """
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.*, r.room_id AS room_name
           FROM devices d JOIN rooms r ON d.room_id = r.id
           ORDER BY r.room_id, d.device_name"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_devices(keyword):
    """Search for devices by room ID, device name, or status.

    Args:
        keyword (str): The search term to match against room_id, device_name,
            and status fields. Matching is case-insensitive and uses partial
            matching.

    Returns:
        list[dict]: A list of dictionaries for devices matching the keyword,
            sorted by room ID and device name.
    """
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
    """Create a new device in the database.

    Args:
        room_id (int): The primary key of the room the device belongs to.
        device_name (str): The name or label of the device.
        status (str): The initial device status. Defaults to 'Active'.
            Must be one of 'Active', 'Inactive', or 'Maintenance'.

    Returns:
        bool: True if the device was created successfully, False if the
            operation failed.
    """
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
    """Update the cabinet password for a specific device.

    Args:
        device_id (int): The primary key of the device to update.
        new_password (str): The new cabinet password to set.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE devices SET cabinet_password=? WHERE id=?",
        (new_password, device_id),
    )
    conn.commit()
    conn.close()


def update_device_status(device_id, status):
    """Update the status of a specific device.

    Args:
        device_id (int): The primary key of the device to update.
        status (str): The new status value. Must be one of 'Active',
            'Inactive', or 'Maintenance'.
    """
    conn = get_connection()
    conn.execute(
        "UPDATE devices SET status=? WHERE id=?",
        (status, device_id),
    )
    conn.commit()
    conn.close()


def delete_device(device_id):
    """Delete a device from the database by primary key.

    Args:
        device_id (int): The primary key of the device to delete.
    """
    conn = get_connection()
    conn.execute("DELETE FROM devices WHERE id=?", (device_id,))
    conn.commit()
    conn.close()


def generate_password():
    """Generate a random 6-digit numeric password.

    Returns:
        str: A string of 6 random digits (e.g., '042917').
    """
    return "".join(random.choices(string.digits, k=6))
