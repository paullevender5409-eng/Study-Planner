import sqlite3
import os
from datetime import date, datetime, time
from config import Config


def get_db_path():
    """Resolve DB path relative to project root."""
    base = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(base)          # models/ → project root
    return os.path.join(parent, Config.DB_PATH)


def _row_factory(cursor, row):
    """
    Convert each SQLite row to a plain dict.
    Automatically parses DATE, DATETIME, and TIME strings to Python objects
    so templates can call .strftime() on them just like with MySQL.
    """
    # Fields that are DATETIME even though their name ends in _date
    DATETIME_FIELDS = {'due_date', 'remind_at', 'created_at', 'updated_at'}

    d = {}
    for i, col in enumerate(cursor.description):
        val  = row[i]
        name = col[0].lower()

        if val is not None and isinstance(val, str):

            # Explicit DATETIME fields first (before suffix checks)
            if name in DATETIME_FIELDS or name.endswith('_at'):
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d %H:%M', '%Y-%m-%d'):
                    try:
                        val = datetime.strptime(val, fmt)
                        break
                    except ValueError:
                        continue

            # Pure DATE fields  →  datetime.date
            elif name.endswith('_date') or name == 'date':
                try:
                    val = datetime.strptime(val, '%Y-%m-%d').date()
                except ValueError:
                    # Might contain a full datetime; try that too
                    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'):
                        try:
                            val = datetime.strptime(val, fmt)
                            break
                        except ValueError:
                            continue

            # TIME fields  →  datetime.time
            elif name.endswith('_time'):
                for fmt in ('%H:%M:%S', '%H:%M'):
                    try:
                        val = datetime.strptime(val, fmt).time()
                        break
                    except ValueError:
                        continue

        d[name] = val
    return d


def get_db():
    """Open a SQLite connection with the custom row factory."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = _row_factory
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def query_db(sql, args=(), one=False, commit=False):
    """
    Execute a SQL query.
    - Use commit=True for INSERT / UPDATE / DELETE  → returns lastrowid.
    - one=True        for SELECT expecting one row   → returns dict or None.
    - Default         for SELECT expecting many rows → returns list of dicts.

    Write %s placeholders just like MySQL; they are converted to ? for SQLite.
    """
    sql = sql.replace('%s', '?')
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        if commit:
            conn.commit()
            return cur.lastrowid
        rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
