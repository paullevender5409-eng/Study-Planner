from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import login_required
from models.db import query_db
from datetime import datetime

reminders_bp = Blueprint('reminders', __name__, url_prefix='/reminders')

@reminders_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    reminders = query_db(
        """SELECT r.*, t.title as task_title
           FROM reminders r
           LEFT JOIN tasks t ON r.related_task_id = t.id
           WHERE r.user_id=%s ORDER BY r.remind_at ASC""",
        (user_id,)
    )
    tasks = query_db('SELECT id, title FROM tasks WHERE user_id=%s ORDER BY title', (user_id,))
    now = datetime.now()
    return render_template('reminders/index.html', reminders=reminders, tasks=tasks, now=now)


@reminders_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id = session['user_id']
    tasks = query_db('SELECT id, title FROM tasks WHERE user_id=%s ORDER BY title', (user_id,))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        remind_at = request.form.get('remind_at', '')
        related_task_id = request.form.get('related_task_id') or None

        if not title or not remind_at:
            flash('Title and reminder time are required.', 'danger')
            return render_template('reminders/form.html', reminder=None, tasks=tasks)

        query_db(
            'INSERT INTO reminders (user_id, title, message, remind_at, related_task_id) VALUES (%s,%s,%s,%s,%s)',
            (user_id, title, message, remind_at, related_task_id),
            commit=True
        )
        flash('Reminder set!', 'success')
        return redirect(url_for('reminders.index'))

    return render_template('reminders/form.html', reminder=None, tasks=tasks)


@reminders_bp.route('/edit/<int:reminder_id>', methods=['GET', 'POST'])
@login_required
def edit(reminder_id):
    user_id = session['user_id']
    reminder = query_db('SELECT * FROM reminders WHERE id=%s AND user_id=%s', (reminder_id, user_id), one=True)
    if not reminder:
        flash('Reminder not found.', 'danger')
        return redirect(url_for('reminders.index'))

    tasks = query_db('SELECT id, title FROM tasks WHERE user_id=%s ORDER BY title', (user_id,))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        remind_at = request.form.get('remind_at', '')
        related_task_id = request.form.get('related_task_id') or None

        query_db(
            'UPDATE reminders SET title=%s, message=%s, remind_at=%s, related_task_id=%s WHERE id=%s AND user_id=%s',
            (title, message, remind_at, related_task_id, reminder_id, user_id),
            commit=True
        )
        flash('Reminder updated!', 'success')
        return redirect(url_for('reminders.index'))

    return render_template('reminders/form.html', reminder=reminder, tasks=tasks)


@reminders_bp.route('/delete/<int:reminder_id>', methods=['POST'])
@login_required
def delete(reminder_id):
    user_id = session['user_id']
    query_db('DELETE FROM reminders WHERE id=%s AND user_id=%s', (reminder_id, user_id), commit=True)
    flash('Reminder deleted.', 'info')
    return redirect(url_for('reminders.index'))


@reminders_bp.route('/mark-seen/<int:reminder_id>', methods=['POST'])
@login_required
def mark_seen(reminder_id):
    user_id = session['user_id']
    query_db('UPDATE reminders SET is_seen=1 WHERE id=%s AND user_id=%s', (reminder_id, user_id), commit=True)
    return redirect(url_for('reminders.index'))
