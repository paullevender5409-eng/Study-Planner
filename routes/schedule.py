from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from routes.auth import login_required
from models.db import query_db
from datetime import date

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

@schedule_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    filter_date    = request.args.get('date', '')
    filter_subject = request.args.get('subject', '')

    sql    = """SELECT ss.*, s.name as subject_name, s.color
                FROM study_sessions ss
                LEFT JOIN subjects s ON ss.subject_id = s.id
                WHERE ss.user_id=%s"""
    params = [user_id]

    if filter_date:
        sql += ' AND ss.session_date=%s'
        params.append(filter_date)
    if filter_subject:
        sql += ' AND ss.subject_id=%s'
        params.append(filter_subject)

    sql += ' ORDER BY ss.session_date DESC, ss.start_time DESC'
    sessions  = query_db(sql, tuple(params))
    subjects  = query_db('SELECT * FROM subjects WHERE user_id=%s ORDER BY name', (user_id,))
    today     = date.today().strftime('%Y-%m-%d')

    return render_template('schedule/index.html',
        sessions=sessions, subjects=subjects,
        filter_date=filter_date, filter_subject=filter_subject, today=today)


@schedule_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id  = session['user_id']
    subjects = query_db('SELECT * FROM subjects WHERE user_id=%s ORDER BY name', (user_id,))

    if request.method == 'POST':
        subject_id   = request.form.get('subject_id') or None
        topic        = request.form.get('topic', '').strip()
        session_date = request.form.get('session_date', '')
        start_time   = request.form.get('start_time', '')
        end_time     = request.form.get('end_time', '')
        study_type   = request.form.get('study_type', 'Reading')
        priority     = request.form.get('priority', 'Medium')
        notes        = request.form.get('notes', '').strip()

        if not all([session_date, start_time, end_time]):
            flash('Date, start time, and end time are required.', 'danger')
            return render_template('schedule/form.html', study_session=None, subjects=subjects,
                                   today=date.today().strftime('%Y-%m-%d'))
        if start_time >= end_time:
            flash('End time must be after start time.', 'danger')
            return render_template('schedule/form.html', study_session=None, subjects=subjects,
                                   today=date.today().strftime('%Y-%m-%d'))

        # Normalise times to HH:MM:SS
        if len(start_time) == 5: start_time += ':00'
        if len(end_time)   == 5: end_time   += ':00'

        query_db(
            'INSERT INTO study_sessions '
            '(user_id,subject_id,topic,session_date,start_time,end_time,study_type,priority,notes) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (user_id, subject_id, topic, session_date, start_time, end_time,
             study_type, priority, notes),
            commit=True)
        flash('Study session added!', 'success')
        return redirect(url_for('schedule.index'))

    return render_template('schedule/form.html', study_session=None, subjects=subjects,
                           today=date.today().strftime('%Y-%m-%d'))


@schedule_bp.route('/edit/<int:session_id>', methods=['GET', 'POST'])
@login_required
def edit(session_id):
    user_id = session['user_id']
    sess    = query_db('SELECT * FROM study_sessions WHERE id=%s AND user_id=%s',
                       (session_id, user_id), one=True)
    if not sess:
        flash('Session not found.', 'danger')
        return redirect(url_for('schedule.index'))

    subjects = query_db('SELECT * FROM subjects WHERE user_id=%s ORDER BY name', (user_id,))

    if request.method == 'POST':
        subject_id   = request.form.get('subject_id') or None
        topic        = request.form.get('topic', '').strip()
        session_date = request.form.get('session_date', '')
        start_time   = request.form.get('start_time', '')
        end_time     = request.form.get('end_time', '')
        study_type   = request.form.get('study_type', 'Reading')
        priority     = request.form.get('priority', 'Medium')
        notes        = request.form.get('notes', '').strip()
        is_completed = 1 if request.form.get('is_completed') else 0

        if len(start_time) == 5: start_time += ':00'
        if len(end_time)   == 5: end_time   += ':00'

        query_db(
            'UPDATE study_sessions SET subject_id=%s,topic=%s,session_date=%s,'
            'start_time=%s,end_time=%s,study_type=%s,priority=%s,notes=%s,is_completed=%s '
            'WHERE id=%s AND user_id=%s',
            (subject_id, topic, session_date, start_time, end_time,
             study_type, priority, notes, is_completed, session_id, user_id),
            commit=True)
        flash('Session updated!', 'success')
        return redirect(url_for('schedule.index'))

    return render_template('schedule/form.html', study_session=sess, subjects=subjects,
                           today=date.today().strftime('%Y-%m-%d'))


@schedule_bp.route('/complete/<int:session_id>', methods=['POST'])
@login_required
def complete(session_id):
    user_id = session['user_id']
    query_db('UPDATE study_sessions SET is_completed=1 WHERE id=%s AND user_id=%s',
             (session_id, user_id), commit=True)
    flash('Session marked as completed!', 'success')
    return redirect(url_for('schedule.index'))


@schedule_bp.route('/delete/<int:session_id>', methods=['POST'])
@login_required
def delete(session_id):
    user_id = session['user_id']
    query_db('DELETE FROM study_sessions WHERE id=%s AND user_id=%s',
             (session_id, user_id), commit=True)
    flash('Session deleted.', 'info')
    return redirect(url_for('schedule.index'))
