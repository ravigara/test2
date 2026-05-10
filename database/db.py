"""
SQLite database layer for Mitra Mental Wellness Companion.
All CRUD operations for checkins, journals, suggestions, and user profile.
"""

import sqlite3
import json
import os
import tempfile
from datetime import datetime, date, timedelta
from pathlib import Path

def _get_db_path() -> Path:
    """
    Returns a persistent local database path when running on Windows (laptop),
    or a session-isolated temporary database path when running on Linux (Streamlit Cloud).
    This ensures multiple users online don't see each other's data.
    """
    if os.name == 'nt':
        return Path(__file__).parent.parent / "data" / "mitra.db"
    
    try:
        from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
        ctx = get_script_run_ctx()
        session_id = ctx.session_id if ctx else "default"
    except ImportError:
        session_id = "default"
        
    return Path(tempfile.gettempdir()) / f"mitra_{session_id}.db"


def _get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    is_new = not db_path.exists()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    if is_new:
        cursor = conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS checkins (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
                date            DATE,
                detected_mood   TEXT,
                self_mood       TEXT,
                mood_score      INTEGER,
                stress_level    TEXT,
                energy_level    TEXT,
                notes           TEXT,
                ai_response     TEXT
            );
            CREATE TABLE IF NOT EXISTS journal_entries (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
                date            DATE,
                content         TEXT,
                sentiment       TEXT,
                themes          TEXT,
                ai_reflection   TEXT
            );
            CREATE TABLE IF NOT EXISTS wellness_suggestions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                date            DATE,
                trigger_mood    TEXT,
                suggestions     TEXT,
                category        TEXT
            );
            CREATE TABLE IF NOT EXISTS user_profile (
                key             TEXT PRIMARY KEY,
                value           TEXT
            );
        """)
        conn.commit()
    
    return conn


def init_db():
    """Create all tables if they do not exist."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS checkins (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
            date            DATE,
            detected_mood   TEXT,
            self_mood       TEXT,
            mood_score      INTEGER,
            stress_level    TEXT,
            energy_level    TEXT,
            notes           TEXT,
            ai_response     TEXT
        );

        CREATE TABLE IF NOT EXISTS journal_entries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
            date            DATE,
            content         TEXT,
            sentiment       TEXT,
            themes          TEXT,
            ai_reflection   TEXT
        );

        CREATE TABLE IF NOT EXISTS wellness_suggestions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            date            DATE,
            trigger_mood    TEXT,
            suggestions     TEXT,
            category        TEXT
        );

        CREATE TABLE IF NOT EXISTS user_profile (
            key             TEXT PRIMARY KEY,
            value           TEXT
        );
    """)
    conn.commit()
    conn.close()


def save_checkin(data: dict) -> int:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO checkins (date, detected_mood, self_mood, mood_score,
                              stress_level, energy_level, notes, ai_response)
        VALUES (:date, :detected_mood, :self_mood, :mood_score,
                :stress_level, :energy_level, :notes, :ai_response)
    """, data)
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_journal(data: dict) -> int:
    conn = _get_connection()
    cursor = conn.cursor()
    if isinstance(data.get("themes"), list):
        data = dict(data)
        data["themes"] = json.dumps(data["themes"])
    cursor.execute("""
        INSERT INTO journal_entries (date, content, sentiment, themes, ai_reflection)
        VALUES (:date, :content, :sentiment, :themes, :ai_reflection)
    """, data)
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return row_id


def save_suggestions(data: dict):
    conn = _get_connection()
    cursor = conn.cursor()
    if isinstance(data.get("suggestions"), list):
        data = dict(data)
        data["suggestions"] = json.dumps(data["suggestions"])
    cursor.execute("""
        INSERT INTO wellness_suggestions (date, trigger_mood, suggestions, category)
        VALUES (:date, :trigger_mood, :suggestions, :category)
    """, data)
    conn.commit()
    conn.close()


def get_checkins(days: int = 7) -> list[dict]:
    conn = _get_connection()
    cursor = conn.cursor()
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    cursor.execute("""
        SELECT * FROM checkins WHERE date >= ? ORDER BY timestamp DESC
    """, (cutoff,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_journals(days: int = 7) -> list[dict]:
    conn = _get_connection()
    cursor = conn.cursor()
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    cursor.execute("""
        SELECT * FROM journal_entries WHERE date >= ? ORDER BY timestamp DESC
    """, (cutoff,))
    rows = []
    for r in cursor.fetchall():
        row = dict(r)
        try:
            row["themes"] = json.loads(row["themes"]) if row["themes"] else []
        except Exception:
            row["themes"] = []
        rows.append(row)
    conn.close()
    return rows


def get_streak() -> int:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT date FROM checkins ORDER BY date DESC
    """)
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not dates:
        return 0

    streak = 0
    check_date = date.today()
    for d_str in dates:
        try:
            d = date.fromisoformat(d_str)
        except Exception:
            continue
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d - timedelta(days=1)
        else:
            break
    return streak


def get_user_profile(key: str) -> str:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""


def set_user_profile(key: str, value: str):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_profile (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_today_checkin() -> dict | None:
    conn = _get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("""
        SELECT * FROM checkins WHERE date = ? ORDER BY timestamp DESC LIMIT 1
    """, (today,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_longest_streak() -> int:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM checkins ORDER BY date ASC")
    dates = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not dates:
        return 0

    max_streak = 1
    current = 1
    for i in range(1, len(dates)):
        try:
            prev = date.fromisoformat(dates[i - 1])
            curr = date.fromisoformat(dates[i])
            if (curr - prev).days == 1:
                current += 1
                max_streak = max(max_streak, current)
            else:
                current = 1
        except Exception:
            current = 1
    return max_streak


def get_total_checkins() -> int:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM checkins")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_avg_mood_score() -> float:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(mood_score) FROM checkins")
    avg = cursor.fetchone()[0]
    conn.close()
    return round(avg, 1) if avg else 0.0


def clear_all_data():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        DELETE FROM checkins;
        DELETE FROM journal_entries;
        DELETE FROM wellness_suggestions;
        DELETE FROM user_profile;
    """)
    conn.commit()
    conn.close()


def get_wellness_suggestions_for_date(target_date: str) -> list[dict]:
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM wellness_suggestions WHERE date = ? ORDER BY id DESC LIMIT 1
    """, (target_date,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return []
    row = dict(row)
    try:
        return json.loads(row["suggestions"])
    except Exception:
        return []
