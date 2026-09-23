from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.db import query_db
from datetime import date, datetime

dashboard_bp = Blueprint('dashboard', __name__)

# Duration helper (minutes between two HH:MM:SS times on same date)
DURATION_EXPR = (
    "CAST((julianday(session_date || ' ' || end_time) "
    "- julianday(session_date || ' ' || start_time)) * 24 * 60 AS INTEGER)"
)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session['user_id']
    today   = date.today().strftime('%Y-%m-%d')

    # ── Stat counts ───────────────────────────────────────────────────────
    total_subjects = query_db(
        'SELECT COUNT(*) as cnt FROM subjects WHERE user_id=%s', (user_id,), one=True)['cnt']

    today_sessions = query_db(
        'SELECT COUNT(*) as cnt FROM study_sessions WHERE user_id=%s AND session_date=%s',
        (user_id, today), one=True)['cnt']

    pending_tasks = query_db(
        "SELECT COUNT(*) as cnt FROM tasks WHERE user_id=%s AND status IN ('Pending','In Progress')",
        (user_id,), one=True)['cnt']

    completed_tasks = query_db(
        "SELECT COUNT(*) as cnt FROM tasks WHERE user_id=%s AND status='Completed'",
        (user_id,), one=True)['cnt']

    overdue_tasks_count = query_db(
        "SELECT COUNT(*) as cnt FROM tasks WHERE user_id=%s AND status='Overdue'",
        (user_id,), one=True)['cnt']

    total_tasks = query_db(
        'SELECT COUNT(*) as cnt FROM tasks WHERE user_id=%s', (user_id,), one=True)['cnt']

    # ── Total study hours ─────────────────────────────────────────────────
    hours_row = query_db(
        f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins "
        "FROM study_sessions WHERE user_id=%s AND is_completed=1",
        (user_id,), one=True)
    total_hours = round((hours_row['mins'] or 0) / 60, 1)

    # ── Progress % ────────────────────────────────────────────────────────
    progress_pct = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)

    # ── Today's schedule ──────────────────────────────────────────────────
    today_schedule = query_db(
        """SELECT ss.*, s.name as subject_name, s.color
           FROM study_sessions ss
           LEFT JOIN subjects s ON ss.subject_id = s.id
           WHERE ss.user_id=%s AND ss.session_date=%s
           ORDER BY ss.start_time""",
        (user_id, today))

    # ── Upcoming deadlines (next 7 days) ──────────────────────────────────
    upcoming = query_db(
        """SELECT t.*, s.name as subject_name
           FROM tasks t
           LEFT JOIN subjects s ON t.subject_id = s.id
           WHERE t.user_id=%s
             AND t.status IN ('Pending','In Progress')
             AND t.due_date >= datetime('now','localtime')
             AND t.due_date <= datetime('now','localtime','+7 days')
           ORDER BY t.due_date ASC LIMIT 5""",
        (user_id,))

    # ── Overdue tasks ─────────────────────────────────────────────────────
    overdue = query_db(
        """SELECT t.*, s.name as subject_name
           FROM tasks t
           LEFT JOIN subjects s ON t.subject_id = s.id
           WHERE t.user_id=%s
             AND (t.status='Overdue'
                  OR (t.status IN ('Pending','In Progress')
                      AND t.due_date < datetime('now','localtime')))
           ORDER BY t.due_date ASC LIMIT 5""",
        (user_id,))

    # ── Notifications (unread) ────────────────────────────────────────────
    notifications = query_db(
        "SELECT * FROM notifications WHERE user_id=%s AND is_read=0 ORDER BY created_at DESC LIMIT 5",
        (user_id,))

    # ── Weekly chart data (last 7 days) ───────────────────────────────────
    weekly_data = query_db(
        f"""SELECT session_date,
               ROUND(SUM({DURATION_EXPR}) / 60.0, 2) as hours
           FROM study_sessions
           WHERE user_id=%s AND is_completed=1
             AND session_date >= date('now','localtime','-6 days')
           GROUP BY session_date ORDER BY session_date""",
        (user_id,))

    return render_template('dashboard.html',
        total_subjects=total_subjects,
        today_sessions=today_sessions,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks_count=overdue_tasks_count,
        total_hours=total_hours,
        progress_pct=progress_pct,
        today_schedule=today_schedule,
        upcoming=upcoming,
        overdue=overdue,
        notifications=notifications,
        weekly_data=weekly_data,
        today=today,
        now=datetime.now()
    )
