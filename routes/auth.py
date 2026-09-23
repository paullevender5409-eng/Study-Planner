from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import bcrypt
from models.db import query_db

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        college = request.form.get('college', '').strip()
        course = request.form.get('course', 'B.Sc. Computer Science').strip()
        year = request.form.get('year', 'TY B.Sc.').strip()
        phone = request.form.get('phone', '').strip()

        if not all([name, email, password, confirm]):
            flash('Please fill all required fields.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')

        existing = query_db('SELECT id FROM users WHERE email=%s', (email,), one=True)
        if existing:
            flash('Email already registered. Please login.', 'danger')
            return render_template('auth/register.html')

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query_db(
            'INSERT INTO users (name, email, password_hash, college, course, year, phone) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (name, email, hashed, college, course, year, phone),
            commit=True
        )
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return render_template('auth/login.html')

        try:
            user = query_db('SELECT * FROM users WHERE email=%s', (email,), one=True)
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Authentication error: {str(e)}', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
