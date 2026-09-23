import os
from flask import Flask, redirect, url_for
from config import Config
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.subjects import subjects_bp
from routes.schedule import schedule_bp
from routes.tasks import tasks_bp
from routes.reminders import reminders_bp
from routes.progress import progress_bp
from routes.reports import reports_bp
from routes.profile import profile_bp

def init_db_if_missing():
    """Ensure SQLite database and tables exist on startup (essential for cloud platforms like Render)."""
    try:
        from models.db import get_db_path
        import sqlite3
        db_file = get_db_path()
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cur.fetchone()
        conn.close()
        if not table_exists:
            print(f"[DB AUTO-INIT] Database tables missing at {db_file}. Initializing now...")
            from database.init_db import init_db
            init_db(db_file)
            print("[DB AUTO-INIT] Database initialized with demo data successfully!")
    except Exception as e:
        print(f"[DB AUTO-INIT ERROR] Could not verify/initialize DB: {e}")

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    # Auto-initialize database on application startup if tables are absent
    init_db_if_missing()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(profile_bp)

    @app.route('/')
    def home():
        return redirect(url_for('dashboard.index'))

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
