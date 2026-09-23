import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-study-planner-secret-key-2024')
    # SQLite DB file path (relative to project root)
    DB_PATH = os.environ.get('DB_PATH', 'database/study_planner.db')
