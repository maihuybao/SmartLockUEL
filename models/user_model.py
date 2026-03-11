import hashlib
from database import get_connection


def hash_password(password):
    """Hash a plain-text password using SHA-256.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hexadecimal SHA-256 digest of the password.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username, password):
    """Authenticate a user by verifying username and password against the database.

    Args:
        username (str): The username to look up.
        password (str): The plain-text password to verify.

    Returns:
        dict or None: A dictionary containing the user record if authentication
            succeeds, or None if no matching user is found.
    """
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    """Retrieve all users from the database.

    Returns:
        list[dict]: A list of dictionaries, each containing 'id', 'username',
            and 'role' keys for a user.
    """
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username, password, role):
    """Create a new user in the database.

    Args:
        username (str): The unique username for the new user.
        password (str): The plain-text password, which will be hashed before storage.
        role (str): The user role, must be either 'admin' or 'user'.

    Returns:
        bool: True if the user was created successfully, False if the operation
            failed (e.g., duplicate username).
    """
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role),
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def update_user(user_id, username, password, role):
    """Update an existing user record in the database.

    If a non-empty password is provided, the password is updated along with the
    username and role. Otherwise, only the username and role are updated.

    Args:
        user_id (int): The primary key of the user to update.
        username (str): The new username.
        password (str): The new plain-text password. If empty or falsy, the
            existing password is kept.
        role (str): The new role, must be either 'admin' or 'user'.

    Returns:
        bool: True if the update succeeded, False if an error occurred
            (e.g., duplicate username).
    """
    conn = get_connection()
    try:
        if password:
            conn.execute(
                "UPDATE users SET username=?, password=?, role=? WHERE id=?",
                (username, hash_password(password), role, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET username=?, role=? WHERE id=?",
                (username, role, user_id),
            )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def delete_user(user_id):
    """Delete a user from the database by primary key.

    Args:
        user_id (int): The primary key of the user to delete.
    """
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
