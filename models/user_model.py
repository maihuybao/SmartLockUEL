import hashlib
from database import get_connection


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username, password, role):
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
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
