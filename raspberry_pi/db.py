"""
ResQMesh - local persistent storage (SQLite)

Why SQLite and not a cloud database:
ResQMesh's entire premise is working with zero internet connectivity.
A cloud backend (e.g. Supabase) would make incident storage depend on
the Pi having live internet - the opposite of what this project proves.
SQLite is a single local file with no server and no network dependency,
so incidents now survive a dashboard restart or a Pi reboot while the
"no internet required" claim stays completely true.

Cloud sync (e.g. pushing this file to Supabase whenever connectivity
happens to be available) is a reasonable FUTURE roadmap item, and is
intentionally not built here.
"""

import sqlite3
import threading

import config

_lock = threading.Lock()


def _connect():
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            type TEXT,
            message TEXT,
            priority TEXT,
            time TEXT,
            date TEXT,
            timestamp TEXT,
            status TEXT
        )
    """)
    conn.commit()
    return conn


def init_db():
    """Create the database file and table if they do not exist yet."""
    conn = _connect()
    conn.close()


def insert_incident(record):
    """Persist one incident record. Never raises - storage must not
    be allowed to crash the live serial receiver."""
    try:
        with _lock:
            conn = _connect()
            conn.execute(
                """INSERT OR REPLACE INTO incidents
                   (id, name, phone, type, message, priority, time, date, timestamp, status)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (record["id"], record["name"], record["phone"], record["type"],
                 record["message"], record["priority"], record["time"],
                 record["date"], record.get("timestamp", ""), record["status"]),
            )
            conn.commit()
            conn.close()
    except sqlite3.Error as exc:
        print("[db] write failed (non-fatal): {}".format(exc))


def load_recent(limit=None):
    """Return incidents newest-first, for pre-loading the dashboard on startup."""
    limit = limit or config.MAX_HISTORY
    try:
        with _lock:
            conn = _connect()
            cur = conn.execute(
                """SELECT id, name, phone, type, message, priority, time, date,
                          timestamp, status
                   FROM incidents ORDER BY id DESC LIMIT ?""",
                (limit,),
            )
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            conn.close()
            return rows
    except sqlite3.Error as exc:
        print("[db] read failed (non-fatal): {}".format(exc))
        return []


def next_id_after_load():
    """The next incident id to use, continuing on from whatever is stored."""
    rows = load_recent(limit=1)
    return (rows[0]["id"] + 1) if rows else 1


def clear_all():
    with _lock:
        conn = _connect()
        conn.execute("DELETE FROM incidents")
        conn.commit()
        conn.close()
