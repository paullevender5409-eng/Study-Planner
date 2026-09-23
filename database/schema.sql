-- Smart Study Planner - SQLite Schema
-- This file is used by database/init_db.py
-- Do NOT run this directly; use: python database/init_db.py

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    college    TEXT,
    course     TEXT DEFAULT 'B.Sc. Computer Science',
    year       TEXT DEFAULT 'TY B.Sc.',
    phone      TEXT,
    study_goal TEXT,
    preferred_hours REAL DEFAULT 4.0,
    created_at TEXT DEFAULT (datetime('now','localtime')),
    updated_at TEXT DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS subjects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    name       TEXT NOT NULL,
    code       TEXT,
    teacher    TEXT,
    semester   TEXT,
    credits    INTEGER DEFAULT 0,
    color      TEXT DEFAULT '#4f46e5',
    created_at TEXT DEFAULT (datetime('now','localtime')),
    updated_at TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    subject_id     INTEGER,
    topic          TEXT,
    session_date   TEXT NOT NULL,   -- stored as YYYY-MM-DD
    start_time     TEXT NOT NULL,   -- stored as HH:MM:SS
    end_time       TEXT NOT NULL,   -- stored as HH:MM:SS
    study_type     TEXT DEFAULT 'Reading',
    priority       TEXT DEFAULT 'Medium',
    notes          TEXT,
    is_completed   INTEGER DEFAULT 0,
    created_at     TEXT DEFAULT (datetime('now','localtime')),
    updated_at     TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    subject_id  INTEGER,
    title       TEXT NOT NULL,
    description TEXT,
    task_type   TEXT DEFAULT 'Assignment',
    due_date    TEXT,               -- stored as YYYY-MM-DD HH:MM:SS
    priority    TEXT DEFAULT 'Medium',
    status      TEXT DEFAULT 'Pending',
    created_at  TEXT DEFAULT (datetime('now','localtime')),
    updated_at  TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS reminders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    title           TEXT NOT NULL,
    message         TEXT,
    remind_at       TEXT NOT NULL,  -- stored as YYYY-MM-DD HH:MM:SS
    is_seen         INTEGER DEFAULT 0,
    related_task_id INTEGER,
    created_at      TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id)          REFERENCES users(id)  ON DELETE CASCADE,
    FOREIGN KEY (related_task_id)  REFERENCES tasks(id)  ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    message    TEXT NOT NULL,
    type       TEXT DEFAULT 'info',
    is_read    INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
