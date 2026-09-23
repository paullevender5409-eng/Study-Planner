from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import login_required
from models.db import query_db
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')

# Priority sort order for SQLite (replaces MySQL's FIELD())
PRIORITY_ORDER = (
    "CASE t.priority "
    "WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END"
)


def update_overdue(user_id):
    """Auto-mark Pending/In Progress tasks as Overdue if past due date."""
    query_db(
        "UPDATE tasks SET status='Overdue' "
        "WHERE user_id=%s AND status IN ('Pending','In Progress') "
        "AND due_date < datetime('now','localtime')",
        (user_id,), commit=True)


@tasks_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    update_overdue(user_id)

    search          = request.args.get('search', '')
    status_filter   = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    subject_filter  = request.args.get('subject', '')

    sql    = """SELECT t.*, s.name as subject_name
                FROM tasks t
                LEFT JOIN subjects s ON t.subject_id = s.id
                WHERE t.user_id=%s"""
    params = [user_id]

    if search:
        sql += ' AND (t.title LIKE %s OR t.description LIKE %s)'
        params.extend([f'%{search}%', f'%{search}%'])
    if status_filter:
        sql += ' AND t.status=%s'
        params.append(status_filter)
    if priority_filter:
        sql += ' AND t.priority=%s'
        params.append(priority_filter)
    if subject_filter:
        sql += ' AND t.subject_id=%s'
        params.append(subject_filter)

    sql += f' ORDER BY {PRIORITY_ORDER}, t.due_date ASC'
    tasks    = query_db(sql, tuple(params))
    subjects = query_db('SELECT * FROM subjects WHERE user_id=%s ORDER BY name', (user_id,))

    counts = {
        'all':         query_db('SELECT COUNT(*) as c FROM tasks WHERE user_id=%s',                                   (user_id,), one=True)['c'],
        'pending':     query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='Pending'",              (user_id,), one=True)['c'],
        'in_progress': query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='In Progress'",          (user_id,), one=True)['c'],
        'completed':   query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='Completed'",            (user_id,), one=True)['c'],
        'overdue':     query_db("SELECT COUNT(*) as c FROM tasks WHERE user_id=%s AND status='Overdue'",              (user_id,), one=True)['c'],
    }

    return render_template('tasks/index.html',
        tasks=tasks, subjects=subjects,
        search=search, status_filter=status_filter,
        priority_filter=priority_filter, subject_filter=subject_filter,
        counts=counts, now=datetime.now())


@tasks_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    user_id  = session['user_id']
    subjects = query_db('SELECT * FROM subjects WHERE user_id=%s ORDER BY name', (user_id,))

    if request.method == 'POST':
        subject_id  = request.form.get('subject_id') or None
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        task_type   = request.form.get('task_type', 'Assignment')
        due_date    = request.form.get('due_date', '').replace('T', ' ') or None
        priority    = request.form.get('priority', 'Medium')
        status      = request.form.get('status', 'Pending')

        if not title:
            flash('Task title is required.', 'danger')
            return render_template('tasks/form.html', task=None, subjects=subjects)

        query_db(
            'INSERT INTO tasks '
            '(user_id,subject_id,title,description,task_type,due_date,priority,status) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (user_id, subject_id, title, description, task_type, due_date, priority, status),
            commit=True)
        flash(f'Task "{title}" added!', 'success')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/form.html', task=None, subjects=subjects)


@tasks_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    user_id = session['user_id']
    task    = query_db('SELECT * FROM tasks WHERE id=%s AND user_id=%s',
                       (task_id, user_id), one=True)
    if not task:
        flash('Task not found.', 'danger')
        return redirect(url_for('tasks.index'))

    subjects = query_db('SELECT * FROM subjects WHERE user_id=%s ORDER BY name', (user_id,))

    if request.method == 'POST':
        subject_id  = request.form.get('subject_id') or None
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        task_type   = request.form.get('task_type', 'Assignment')
        due_date    = request.form.get('due_date', '').replace('T', ' ') or None
        priority    = request.form.get('priority', 'Medium')
        status      = request.form.get('status', 'Pending')

        query_db(
            'UPDATE tasks SET subject_id=%s,title=%s,description=%s,task_type=%s,'
            'due_date=%s,priority=%s,status=%s WHERE id=%s AND user_id=%s',
            (subject_id, title, description, task_type, due_date, priority, status,
             task_id, user_id),
            commit=True)
        flash('Task updated!', 'success')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/form.html', task=task, subjects=subjects)


@tasks_bp.route('/complete/<int:task_id>', methods=['POST'])
@login_required
def complete(task_id):
    user_id = session['user_id']
    query_db("UPDATE tasks SET status='Completed' WHERE id=%s AND user_id=%s",
             (task_id, user_id), commit=True)
    flash('Task marked as completed!', 'success')
    return redirect(url_for('tasks.index'))


@tasks_bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete(task_id):
    user_id = session['user_id']
    task    = query_db('SELECT title FROM tasks WHERE id=%s AND user_id=%s',
                       (task_id, user_id), one=True)
    if task:
        query_db('DELETE FROM tasks WHERE id=%s AND user_id=%s',
                 (task_id, user_id), commit=True)
        flash(f'Task "{task["title"]}" deleted.', 'info')
    else:
        flash('Task not found.', 'danger')
    return redirect(url_for('tasks.index'))
