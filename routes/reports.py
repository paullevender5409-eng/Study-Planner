from flask import Blueprint, render_template, session
from routes.auth import login_required
from models.db import query_db
from datetime import date, timedelta

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

DURATION_EXPR = (
    "CAST((julianday(session_date || ' ' || end_time) "
    "- julianday(session_date || ' ' || start_time)) * 24 * 60 AS INTEGER)"
)

@reports_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    today   = date.today()

    # ── Subject-wise hours ────────────────────────────────────────────────
    subject_hours = query_db(
        f"""SELECT s.name, s.color,
               ROUND(COALESCE(SUM({DURATION_EXPR}),0) / 60.0, 1) as hours,
               COUNT(DISTINCT ss.id) as session_count
            FROM subjects s
            LEFT JOIN study_sessions ss
                ON ss.subject_id=s.id AND ss.user_id=s.user_id AND ss.is_completed=1
            WHERE s.user_id=%s
            GROUP BY s.id, s.name, s.color""",
        (user_id,))

    # ── Weekly (last 7 days) ──────────────────────────────────────────────
    weekly_labels     = []
    weekly_hours_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        row = query_db(
            f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins "
            "FROM study_sessions WHERE user_id=%s AND is_completed=1 AND session_date=%s",
            (user_id, d.strftime('%Y-%m-%d')), one=True)
        weekly_labels.append(d.strftime('%a, %b %d'))
        weekly_hours_data.append(round((row['mins'] or 0) / 60, 2))

    # ── Task status breakdown ─────────────────────────────────────────────
    task_status = query_db(
        'SELECT status, COUNT(*) as cnt FROM tasks WHERE user_id=%s GROUP BY status',
        (user_id,))

    # ── Monthly (last 6 months) ───────────────────────────────────────────
    monthly_labels  = []
    monthly_hours   = []
    monthly_sessions = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        m_start = date(y, m, 1)
        m_end   = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        row = query_db(
            f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins, COUNT(*) as cnt "
            "FROM study_sessions WHERE user_id=%s AND is_completed=1 "
            "AND session_date >= %s AND session_date < %s",
            (user_id, m_start.strftime('%Y-%m-%d'), m_end.strftime('%Y-%m-%d')), one=True)
        monthly_labels.append(m_start.strftime('%b %Y'))
        monthly_hours.append(round((row['mins'] or 0) / 60, 1))
        monthly_sessions.append(row['cnt'] or 0)

    # ── Study type distribution ───────────────────────────────────────────
    type_distribution = query_db(
        'SELECT study_type, COUNT(*) as cnt FROM study_sessions '
        'WHERE user_id=%s AND is_completed=1 GROUP BY study_type',
        (user_id,))

    # ── Summary stats ─────────────────────────────────────────────────────
    total_tasks     = query_db('SELECT COUNT(*) as c FROM tasks WHERE user_id=%s', (user_id,), one=True)['c']
    completed_tasks = query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='Completed'", (user_id,), one=True)['c']
    hrs_row         = query_db(
        f"SELECT COALESCE(SUM({DURATION_EXPR}),0) as mins "
        "FROM study_sessions WHERE user_id=%s AND is_completed=1",
        (user_id,), one=True)
    total_hours = round((hrs_row['mins'] or 0) / 60, 1)
    avg_daily   = round(total_hours / 30, 1)

    return render_template('reports.html',
        subject_hours=subject_hours,
        weekly_labels=weekly_labels,
        weekly_hours_data=weekly_hours_data,
        task_status=task_status,
        monthly_labels=monthly_labels,
        monthly_hours=monthly_hours,
        monthly_sessions=monthly_sessions,
        type_distribution=type_distribution,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        total_hours=total_hours,
        avg_daily=avg_daily
    )
