import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "atlas_memory.db"


def get_connection():
    """Create a connection to the Atlas SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create required Atlas tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # User profile / memory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            role TEXT,
            interests TEXT,
            watchlist TEXT,
            last_updated TEXT
        )
    """)

    # Conversation memory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT,
            assistant_message TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_user_profile(user_id: str) -> dict:
    """
    Return the user's stored profile as a dictionary.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, interests, watchlist
        FROM user_profiles
        WHERE user_id = ?
    """, (str(user_id),))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {
            "role": "Unknown",
            "interests": "Unknown",
            "watchlist": ""
        }

    return {
        "role": row[0] or "Unknown",
        "interests": row[1] or "Unknown",
        "watchlist": row[2] or ""
    }


def update_user_profile_data(
    user_id: str,
    role: Optional[str] = None,
    interests: Optional[str] = None,
    watchlist: Optional[str] = None
) -> str:
    """
    Update one or more user profile fields.

    This function is exposed to Gemini automatic function calling,
    so all parameters must have explicit type annotations.
    """

    conn = get_connection()
    cursor = conn.cursor()

    user_id = str(user_id)
    now = datetime.now().isoformat()

    # Make sure the user exists
    cursor.execute("""
        INSERT OR IGNORE INTO user_profiles
        (user_id, role, interests, watchlist, last_updated)
        VALUES (?, NULL, NULL, NULL, ?)
    """, (
        user_id,
        now
    ))

    # Update role
    if role is not None and role.strip():
        cursor.execute("""
            UPDATE user_profiles
            SET role = ?, last_updated = ?
            WHERE user_id = ?
        """, (
            role.strip(),
            now,
            user_id
        ))

    # Update interests
    if interests is not None and interests.strip():
        cursor.execute("""
            UPDATE user_profiles
            SET interests = ?, last_updated = ?
            WHERE user_id = ?
        """, (
            interests.strip(),
            now,
            user_id
        ))

    # Update watchlist
    if watchlist is not None and watchlist.strip():
        cursor.execute("""
            UPDATE user_profiles
            SET watchlist = ?, last_updated = ?
            WHERE user_id = ?
        """, (
            watchlist.strip(),
            now,
            user_id
        ))

    conn.commit()
    conn.close()

    return "Profile successfully updated."


def save_conversation(
    user_id: str,
    user_message: str,
    assistant_message: str
) -> None:
    """
    Save a conversation using the existing database schema.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations
        (
            user_id,
            user_message,
            assistant_message,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        int(user_id),
        str(user_message),
        str(assistant_message),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_recent_conversations(
    user_id: str,
    limit: int = 10
):
    """
    Retrieve recent conversations for future memory features.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_message, assistant_message, created_at
        FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        int(user_id),
        int(limit)
    ))

    rows = cursor.fetchall()
    conn.close()

    return rows


# Initialize database when this module loads
init_db()