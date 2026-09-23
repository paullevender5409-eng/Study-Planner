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

def create_app():
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

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


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8080)
