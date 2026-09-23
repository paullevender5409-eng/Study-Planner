from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import login_required
from models.db import query_db
import bcrypt

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

_DUR = ("CAST((julianday(session_date || ' ' || end_time) "
        "- julianday(session_date || ' ' || start_time)) * 24 * 60 AS INTEGER)")

@profile_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    user = query_db('SELECT * FROM users WHERE id=%s', (user_id,), one=True)
    hrs_row = query_db(
        f"SELECT COALESCE(SUM({_DUR}),0) as mins "
        "FROM study_sessions WHERE user_id=%s AND is_completed=1",
        (user_id,), one=True)
    stats = {
        'subjects': query_db('SELECT COUNT(*) as c FROM subjects WHERE user_id=%s', (user_id,), one=True)['c'],
        'sessions': query_db('SELECT COUNT(*) as c FROM study_sessions WHERE user_id=%s', (user_id,), one=True)['c'],
        'tasks':    query_db('SELECT COUNT(*) as c FROM tasks WHERE user_id=%s', (user_id,), one=True)['c'],
        'hours':    round((hrs_row['mins'] or 0) / 60, 1),
    }
    return render_template('profile.html', user=user, stats=stats)


@profile_bp.route('/edit', methods=['POST'])
@login_required
def edit():
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    college = request.form.get('college', '').strip()
    course = request.form.get('course', '').strip()
    year = request.form.get('year', '').strip()
    phone = request.form.get('phone', '').strip()
    study_goal = request.form.get('study_goal', '').strip()
    preferred_hours = request.form.get('preferred_hours', 4.0)

    if not name:
        flash('Name is required.', 'danger')
        return redirect(url_for('profile.index'))

    query_db(
        'UPDATE users SET name=%s, college=%s, course=%s, year=%s, phone=%s, study_goal=%s, preferred_hours=%s WHERE id=%s',
        (name, college, course, year, phone, study_goal, preferred_hours, user_id),
        commit=True
    )
    session['user_name'] = name
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile.index'))


@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user_id = session['user_id']
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    user = query_db('SELECT password_hash FROM users WHERE id=%s', (user_id,), one=True)

    if not bcrypt.checkpw(current_pw.encode('utf-8'), user['password_hash'].encode('utf-8')):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile.index'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('profile.index'))

    if len(new_pw) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('profile.index'))

    hashed = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    query_db('UPDATE users SET password_hash=%s WHERE id=%s', (hashed, user_id), commit=True)
    flash('Password changed successfully!', 'success')
    return redirect(url_for('profile.index'))
