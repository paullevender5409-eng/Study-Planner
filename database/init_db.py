"""
Smart Study Planner - Database Initialiser
==========================================
Run once to create the SQLite database and insert demo data.

    python database/init_db.py

Safe to re-run: DROP and recreate if you want a fresh start,
or it will skip existing data with INSERT OR IGNORE.
"""

import sqlite3
import bcrypt
import os
import sys
from datetime import date, timedelta, datetime

# Resolve paths
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH   = os.path.join(BASE_DIR, 'database', 'study_planner.db')
SCHEMA    = os.path.join(BASE_DIR, 'database', 'schema.sql')

sys.path.insert(0, BASE_DIR)

def d(offset=0):
    """Return date string offset days from today."""
    return (date.today() + timedelta(days=offset)).strftime('%Y-%m-%d')

def dt(offset_days=0, hour=9, minute=0):
    """Return datetime string offset days from today at given time."""
    return (datetime.now() + timedelta(days=offset_days)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ).strftime('%Y-%m-%d %H:%M:%S')

def init_db():
    print(f"Initialising database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')

    # Run schema
    with open(SCHEMA, 'r') as f:
        # Filter out comment-only lines and PRAGMA (already executed)
        sql = f.read()
    conn.executescript(sql)
    print("  Schema created.")

    cur = conn.cursor()

    # ── Demo user ──────────────────────────────────────────────────────────
    pw_hash = bcrypt.hashpw(b'Demo@123', bcrypt.gensalt(12)).decode('utf-8')
    cur.execute("""
        INSERT OR IGNORE INTO users
            (name, email, password_hash, college, course, year, phone, study_goal, preferred_hours)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (
        'Pranali Kharat',
        'pranali@example.com',
        pw_hash,
        'Pune University',
        'B.Sc. Computer Science',
        'TY B.Sc.',
        '9876543210',
        'Score distinction in all subjects and complete final year project by March.',
        5.0
    ))
    conn.commit()

    user = cur.execute("SELECT id FROM users WHERE email='pranali@example.com'").fetchone()
    user_id = user[0]
    print(f"  Demo user ready  (id={user_id})")

    # ── Subjects ───────────────────────────────────────────────────────────
    subjects = [
        (user_id, 'Advanced Algorithms',   'CS301', 'Dr. Sharma',  'Semester V', 4, '#4f46e5'),
        (user_id, 'Database Management',   'CS302', 'Prof. Mehta',  'Semester V', 4, '#0891b2'),
        (user_id, 'Web Technologies',      'CS303', 'Mrs. Joshi',   'Semester V', 3, '#059669'),
        (user_id, 'Machine Learning',      'CS304', 'Dr. Patel',    'Semester V', 4, '#d97706'),
        (user_id, 'Software Engineering',  'CS305', 'Prof. Desai',  'Semester V', 3, '#dc2626'),
    ]
    cur.executemany("""
        INSERT OR IGNORE INTO subjects (user_id,name,code,teacher,semester,credits,color)
        VALUES (?,?,?,?,?,?,?)
    """, subjects)
    conn.commit()

    sub_ids = {row[0]: row[1] for row in
               cur.execute("SELECT name, id FROM subjects WHERE user_id=?", (user_id,)).fetchall()}
    alg = sub_ids.get('Advanced Algorithms')
    db  = sub_ids.get('Database Management')
    web = sub_ids.get('Web Technologies')
    ml  = sub_ids.get('Machine Learning')
    se  = sub_ids.get('Software Engineering')
    print(f"  Subjects inserted: {list(sub_ids.keys())}")

    # ── Study Sessions ─────────────────────────────────────────────────────
    sessions = [
        # Completed - past week
        (user_id, alg, 'Dynamic Programming',       d(-6), '09:00:00', '11:00:00', 'Practice',  'High',   'Solved 10 DP problems on LeetCode', 1),
        (user_id, db,  'Normalization & ER Diagrams',d(-5), '14:00:00', '16:00:00', 'Reading',   'Medium', 'Covered 1NF, 2NF, 3NF', 1),
        (user_id, web, 'React Hooks and State',      d(-4), '10:00:00', '12:30:00', 'Practice',  'High',   'Built a todo app with hooks', 1),
        (user_id, ml,  'Linear Regression',          d(-3), '15:00:00', '17:00:00', 'Reading',   'Medium', 'Read chapter 3 from textbook', 1),
        (user_id, se,  'SDLC Models',                d(-2), '09:00:00', '10:30:00', 'Revision',  'Low',    'Revised Waterfall and Agile', 1),
        (user_id, alg, 'Graph Algorithms',           d(-1), '11:00:00', '13:00:00', 'Practice',  'High',   'Dijkstra and BFS', 1),
        # Today
        (user_id, db,  'SQL Queries and Joins',      d(0),  '09:00:00', '11:00:00', 'Practice',  'High',   'Practice complex JOIN queries', 0),
        (user_id, web, 'Flask & REST APIs',          d(0),  '14:00:00', '16:00:00', 'Project',   'High',   'Build study planner API', 0),
        # Future
        (user_id, ml,  'Logistic Regression',        d(1),  '10:00:00', '12:00:00', 'Reading',   'Medium', 'Binary classification', 0),
        (user_id, se,  'Design Patterns',            d(2),  '09:00:00', '10:30:00', 'Reading',   'Medium', 'MVC and Observer pattern', 0),
        (user_id, alg, 'Exam Revision – Algorithms', d(3),  '08:00:00', '11:00:00', 'Exam Prep', 'High',   'Full revision before unit test', 0),
        (user_id, db,  'Database Project Work',      d(4),  '13:00:00', '15:30:00', 'Project',   'High',   'Complete ER diagram for project', 0),
    ]
    cur.executemany("""
        INSERT INTO study_sessions
            (user_id,subject_id,topic,session_date,start_time,end_time,study_type,priority,notes,is_completed)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, sessions)
    conn.commit()
    print(f"  Study sessions inserted: {len(sessions)}")

    # ── Tasks ──────────────────────────────────────────────────────────────
    tasks = [
        (user_id, db,  'Database Mini Project',        'Design and implement a library management system database',    'Project',      dt(5,  23, 59), 'High',   'In Progress'),
        (user_id, web, 'Web Assignment - Portfolio',   'Create a responsive portfolio website using HTML, CSS, JS',   'Assignment',   dt(3,  23, 59), 'High',   'In Progress'),
        (user_id, ml,  'ML Lab Submission',            'Implement and submit linear regression from scratch',          'Assignment',   dt(7,  23, 59), 'Medium', 'Pending'),
        (user_id, alg, 'Algorithm Assignment 2',       'Solve 5 DP problems and submit report',                       'Homework',     dt(2,  23, 59), 'Urgent', 'Pending'),
        (user_id, se,  'SE Unit Test Preparation',     'Prepare for unit test covering SDLC, UML, Design Patterns',   'Exam',         dt(1,  10,  0), 'Urgent', 'Pending'),
        (user_id, web, 'React Component Assignment',   'Build a multi-step form with React',                          'Assignment',   dt(-2, 23, 59), 'High',   'Overdue'),
        (user_id, db,  'DB Normalization Exercise',    'Normalize given schema to 3NF and BCNF',                      'Homework',     dt(-1, 23, 59), 'Medium', 'Overdue'),
        (user_id, alg, 'Algorithm Lab 1',              'Implement sorting algorithms and compare time complexity',     'Assignment',   dt(-5, 23, 59), 'Low',    'Completed'),
        (user_id, ml,  'ML Quiz 1',                    'Prepare for online quiz on supervised learning',               'Exam',         dt(-3, 23, 59), 'Medium', 'Completed'),
        (user_id, se,  'Software Presentation',        'Group presentation on Agile methodology',                      'Presentation', dt(-4, 23, 59), 'High',   'Completed'),
    ]
    cur.executemany("""
        INSERT INTO tasks
            (user_id,subject_id,title,description,task_type,due_date,priority,status)
        VALUES (?,?,?,?,?,?,?,?)
    """, tasks)
    conn.commit()
    print(f"  Tasks inserted: {len(tasks)}")

    # Fetch task IDs for reminders
    task_rows = cur.execute(
        "SELECT id, title FROM tasks WHERE user_id=?", (user_id,)
    ).fetchall()
    task_map = {row[1]: row[0] for row in task_rows}

    # ── Reminders ──────────────────────────────────────────────────────────
    reminders = [
        (user_id, 'SE Unit Test Tomorrow',    "Don't forget the SE unit test is tomorrow!",        dt(0, 20, 0), task_map.get('SE Unit Test Preparation')),
        (user_id, 'Algorithm Assignment Due', 'Algorithm Assignment 2 is due in 2 days!',          dt(1, 8,  0), task_map.get('Algorithm Assignment 2')),
        (user_id, 'DB Project Deadline',      'Complete the ER diagram for DB Mini Project.',      dt(4, 9,  0), task_map.get('Database Mini Project')),
        (user_id, 'Weekly Study Review',      'Review your study progress for this week.',         dt(2, 18, 0), None),
        (user_id, 'ML Lab Submission',        'ML Lab submission is due next week.',               dt(6, 9,  0), task_map.get('ML Lab Submission')),
    ]
    cur.executemany("""
        INSERT INTO reminders (user_id,title,message,remind_at,related_task_id)
        VALUES (?,?,?,?,?)
    """, reminders)
    conn.commit()
    print(f"  Reminders inserted: {len(reminders)}")

    # ── Notifications ──────────────────────────────────────────────────────
    notifications = [
        (user_id, 'Welcome to Smart Study Planner! Start by adding your subjects.', 'info',    1),
        (user_id, 'You have 2 overdue tasks. Please complete them ASAP.',           'warning', 0),
        (user_id, 'Study session "SQL Queries and Joins" is scheduled for today.',  'info',    0),
        (user_id, 'Great job! You completed Algorithm Lab 1 successfully.',         'success', 1),
    ]
    cur.executemany("""
        INSERT INTO notifications (user_id,message,type,is_read)
        VALUES (?,?,?,?)
    """, notifications)
    conn.commit()
    print(f"  Notifications inserted: {len(notifications)}")

    conn.close()
    print("\n✅ Database initialised successfully!")
    print(f"   File: {DB_PATH}")
    print("\n📋 Demo login:")
    print("   Email   : pranali@example.com")
    print("   Password: Demo@123")


if __name__ == '__main__':
    init_db()
