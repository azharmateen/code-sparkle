"""SQLite storage for XP, achievements, streaks, activity history."""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


DB_DIR = os.path.join(str(Path.home()), ".code-sparkle")
DB_PATH = os.path.join(DB_DIR, "sparkle.db")


def get_db() -> sqlite3.Connection:
    """Get database connection, creating schema if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection):
    """Create all tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_path TEXT UNIQUE NOT NULL,
            username TEXT DEFAULT '',
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            title TEXT DEFAULT 'Beginner',
            last_synced TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            commit_hash TEXT NOT NULL,
            commit_date TEXT NOT NULL,
            message TEXT DEFAULT '',
            lines_added INTEGER DEFAULT 0,
            lines_deleted INTEGER DEFAULT 0,
            files_changed INTEGER DEFAULT 0,
            files TEXT DEFAULT '[]',
            xp_earned INTEGER DEFAULT 0,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
            UNIQUE(profile_id, commit_hash)
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            achievement_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            unlocked_at TEXT NOT NULL,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
            UNIQUE(profile_id, achievement_id)
        );

        CREATE TABLE IF NOT EXISTS streaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            commit_count INTEGER DEFAULT 0,
            FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
            UNIQUE(profile_id, date)
        );
    """)
    conn.commit()


def get_or_create_profile(repo_path: str) -> dict:
    """Get or create a profile for a repository."""
    conn = get_db()
    row = conn.execute("SELECT * FROM profiles WHERE repo_path = ?", (repo_path,)).fetchone()
    if row:
        conn.close()
        return dict(row)

    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO profiles (repo_path, created_at) VALUES (?, ?)", (repo_path, now)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM profiles WHERE repo_path = ?", (repo_path,)).fetchone()
    conn.close()
    return dict(row)


def update_profile_xp(profile_id: int, total_xp: int, level: int, title: str):
    """Update profile XP, level, and title."""
    conn = get_db()
    conn.execute(
        "UPDATE profiles SET total_xp = ?, level = ?, title = ?, last_synced = ? WHERE id = ?",
        (total_xp, level, title, datetime.now().isoformat(), profile_id)
    )
    conn.commit()
    conn.close()


def log_activity(profile_id: int, commit_hash: str, commit_date: str, message: str,
                 lines_added: int, lines_deleted: int, files_changed: int,
                 files: str, xp_earned: int) -> bool:
    """Log a commit activity. Returns False if already logged."""
    conn = get_db()
    try:
        conn.execute(
            """INSERT INTO activity_log
               (profile_id, commit_hash, commit_date, message, lines_added, lines_deleted,
                files_changed, files, xp_earned)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (profile_id, commit_hash, commit_date, message, lines_added, lines_deleted,
             files_changed, files, xp_earned)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_total_xp(profile_id: int) -> int:
    """Get total XP for a profile."""
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(xp_earned), 0) as total FROM activity_log WHERE profile_id = ?",
        (profile_id,)
    ).fetchone()
    conn.close()
    return row["total"]


def get_activity_count(profile_id: int) -> int:
    """Get total activity count."""
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM activity_log WHERE profile_id = ?", (profile_id,)
    ).fetchone()
    conn.close()
    return row["cnt"]


def unlock_achievement(profile_id: int, achievement_id: str, name: str, description: str) -> bool:
    """Unlock an achievement. Returns False if already unlocked."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO achievements (profile_id, achievement_id, name, description, unlocked_at) VALUES (?, ?, ?, ?, ?)",
            (profile_id, achievement_id, name, description, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_achievements(profile_id: int) -> list:
    """Get all unlocked achievements."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM achievements WHERE profile_id = ? ORDER BY unlocked_at DESC", (profile_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_streak_day(profile_id: int, date: str, commit_count: int):
    """Record a streak day."""
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO streaks (profile_id, date, commit_count) VALUES (?, ?, ?)",
        (profile_id, date, commit_count)
    )
    conn.commit()
    conn.close()


def get_streak_days(profile_id: int) -> list:
    """Get all streak days sorted."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM streaks WHERE profile_id = ? ORDER BY date DESC", (profile_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
