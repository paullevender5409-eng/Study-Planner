from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.db import query_db
from datetime import date, timedelta

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

DURATION_EXPR = (
    "CAST((julianday(session_date || ' ' || end_time) "
    "- julianday(session_date || ' ' || start_time)) * 24 * 60 AS INTEGER)"
)

@progress_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    today   = date.today()

    # ── Task counts ───────────────────────────────────────────────────────
    total_tasks     = query_db('SELECT COUNT(*) as c FROM tasks WHERE user_id=%s', (user_id,), one=True)['c']
    completed_tasks = query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='Completed'", (user_id,), one=True)['c']
    overdue_tasks   = query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='Overdue'", (user_id,), one=True)['c']
    pending_tasks   = total_tasks - completed_tasks - overdue_tasks
    completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)

    # ── Total study hours ─────────────────────────────────────────────────
    def _hours(extra_where='', extra_params=()):
        row = query_db(
            f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins "
            f"FROM study_sessions WHERE user_id=%s AND is_completed=1 {extra_where}",
            (user_id,) + extra_params, one=True)
        return round((row['mins'] or 0) / 60, 1)

    total_hours  = _hours()
    week_start   = today - timedelta(days=today.weekday())
    week_hours   = _hours('AND session_date >= %s', (week_start.strftime('%Y-%m-%d'),))
    month_start  = today.replace(day=1)
    month_hours  = _hours('AND session_date >= %s', (month_start.strftime('%Y-%m-%d'),))

    # ── Session counts ────────────────────────────────────────────────────
    total_sessions     = query_db('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=%s', (user_id,), one=True)['c']
    completed_sessions = query_db('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=%s AND is_completed=1', (user_id,), one=True)['c']

    # ── Study streak (consecutive completed days) ─────────────────────────
    streak     = 0
    check_date = today
    while streak <= 365:
        cnt = query_db(
            'SELECT COUNT(*) as c FROM study_sessions WHERE user_id=%s AND session_date=%s AND is_completed=1',
            (user_id, check_date.strftime('%Y-%m-%d')), one=True)['c']
        if cnt > 0:
            streak    += 1
            check_date = check_date - timedelta(days=1)
        else:
            break

    # ── Weekly chart (last 7 days) ────────────────────────────────────────
    weekly_labels     = []
    weekly_hours_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        row = query_db(
            f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins "
            "FROM study_sessions WHERE user_id=%s AND is_completed=1 AND session_date=%s",
            (user_id, d.strftime('%Y-%m-%d')), one=True)
        weekly_labels.append(d.strftime('%a %d'))
        weekly_hours_data.append(round((row['mins'] or 0) / 60, 2))

    # ── Subject-wise hours ────────────────────────────────────────────────
    subject_hours = query_db(
        f"""SELECT s.name, s.color,
               ROUND(COALESCE(SUM({DURATION_EXPR}),0) / 60.0, 1) as hours
            FROM subjects s
            LEFT JOIN study_sessions ss
                ON ss.subject_id=s.id AND ss.user_id=s.user_id AND ss.is_completed=1
            WHERE s.user_id=%s
            GROUP BY s.id, s.name, s.color
            ORDER BY hours DESC""",
        (user_id,))

    # ── Task breakdown by type ────────────────────────────────────────────
    task_by_type = query_db(
        "SELECT task_type, COUNT(*) as total, "
        "SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) as done "
        "FROM tasks WHERE user_id=%s GROUP BY task_type",
        (user_id,))

    # ── Monthly hours (last 6 months) ─────────────────────────────────────
    monthly_data = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        m_start = date(y, m, 1)
        m_end   = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        row = query_db(
            f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins "
            "FROM study_sessions WHERE user_id=%s AND is_completed=1 "
            "AND session_date >= %s AND session_date < %s",
            (user_id, m_start.strftime('%Y-%m-%d'), m_end.strftime('%Y-%m-%d')), one=True)
        monthly_data.append({
            'label': m_start.strftime('%b %Y'),
            'hours': round((row['mins'] or 0) / 60, 1)
        })

    return render_template('progress.html',
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        pending_tasks=pending_tasks,
        completion_rate=completion_rate,
        total_hours=total_hours,
        week_hours=week_hours,
        month_hours=month_hours,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        streak=streak,
        weekly_labels=weekly_labels,
        weekly_hours_data=weekly_hours_data,
        subject_hours=subject_hours,
        task_by_type=task_by_type,
        monthly_data=monthly_data
    )
