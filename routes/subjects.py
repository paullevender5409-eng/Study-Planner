from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import login_required
from models.db import query_db

subjects_bp = Blueprint('subjects', __name__, url_prefix='/subjects')

DURATION_EXPR = (
    "CAST((julianday(ss2.session_date || ' ' || ss2.end_time) "
    "- julianday(ss2.session_date || ' ' || ss2.start_time)) * 24 * 60 AS INTEGER)"
)

@subjects_bp.route('/')
@login_required
def index():
    user_id  = session['user_id']
    subjects = query_db(
        f"""SELECT s.*,
               (SELECT COUNT(*) FROM study_sessions ss  WHERE ss.subject_id=s.id  AND ss.user_id=s.user_id)  as session_count,
               (SELECT COUNT(*) FROM tasks t             WHERE t.subject_id=s.id   AND t.user_id=s.user_id)   as task_count,
               (SELECT ROUND(COALESCE(SUM({DURATION_EXPR}),0)/60.0,1)
                FROM study_sessions ss2
                WHERE ss2.subject_id=s.id AND ss2.user_id=s.user_id AND ss2.is_completed=1)                   as study_hours
            FROM subjects s WHERE s.user_id=%s ORDER BY s.created_at DESC""",
        (user_id,))
    return render_template('subjects/index.html', subjects=subjects)


@subjects_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id = session['user_id']
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        code     = request.form.get('code', '').strip()
        teacher  = request.form.get('teacher', '').strip()
        semester = request.form.get('semester', '').strip()
        credits  = request.form.get('credits', 0)
        color    = request.form.get('color', '#4f46e5')

        if not name:
            flash('Subject name is required.', 'danger')
            return render_template('subjects/form.html', subject=None)

        query_db(
            'INSERT INTO subjects (user_id,name,code,teacher,semester,credits,color) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (user_id, name, code, teacher, semester, credits or 0, color), commit=True)
        flash(f'Subject "{name}" added successfully!', 'success')
        return redirect(url_for('subjects.index'))

    return render_template('subjects/form.html', subject=None)


@subjects_bp.route('/edit/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit(subject_id):
    user_id = session['user_id']
    subject = query_db('SELECT * FROM subjects WHERE id=%s AND user_id=%s',
                       (subject_id, user_id), one=True)
    if not subject:
        flash('Subject not found.', 'danger')
        return redirect(url_for('subjects.index'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        code     = request.form.get('code', '').strip()
        teacher  = request.form.get('teacher', '').strip()
        semester = request.form.get('semester', '').strip()
        credits  = request.form.get('credits', 0)
        color    = request.form.get('color', '#4f46e5')

        if not name:
            flash('Subject name is required.', 'danger')
            return render_template('subjects/form.html', subject=subject)

        query_db(
            'UPDATE subjects SET name=%s,code=%s,teacher=%s,semester=%s,credits=%s,color=%s '
            'WHERE id=%s AND user_id=%s',
            (name, code, teacher, semester, credits or 0, color, subject_id, user_id), commit=True)
        flash(f'Subject "{name}" updated successfully!', 'success')
        return redirect(url_for('subjects.index'))

    return render_template('subjects/form.html', subject=subject)


@subjects_bp.route('/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete(subject_id):
    user_id = session['user_id']
    subject = query_db('SELECT * FROM subjects WHERE id=%s AND user_id=%s',
                       (subject_id, user_id), one=True)
    if not subject:
        flash('Subject not found.', 'danger')
    else:
        query_db('DELETE FROM subjects WHERE id=%s AND user_id=%s',
                 (subject_id, user_id), commit=True)
        flash(f'Subject "{subject["name"]}" deleted.', 'info')
    return redirect(url_for('subjects.index'))
