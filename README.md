# Smart Study Planner

> **Plan Smart. Study Better. Achieve More.**
> A TY B.Sc. Computer Science Final Year Project

A complete web-based Smart Study Planner that helps students organize subjects, study schedules, assignments, reminders, and track academic progress from a unified dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend | Python Flask |
| Database | SQLite (Built-in, zero external setup required) |
| Charts | Chart.js |
| Auth | bcrypt + Flask sessions |

---

## Features

- **Authentication** – Registration, Login, Logout, Password hashing
- **Dashboard** – Dynamic stats, today's schedule, upcoming deadlines, overdue tasks, charts
- **Subjects** – Add, edit, delete subjects with color coding
- **Study Schedule** – Create sessions, mark complete, filter by date/subject
- **Tasks** – CRUD with search/filter, priority, overdue auto-detection
- **Reminders** – In-app reminders linked to tasks
- **Progress** – Study streak, weekly/monthly hours, subject-wise breakdown
- **Reports** – 5 Chart.js charts with detailed analytics
- **Profile** – View/edit profile, change password

---

## Project Structure

```
Study Planner/
├── app.py              # Flask app entry point
├── config.py           # Environment config (SQLite DB path, Secret Key)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── README.md           
├── database/
│   ├── schema.sql      # SQLite schema
│   ├── init_db.py      # SQLite DB initialization & demo data seeder
│   └── study_planner.db# SQLite database file
├── models/
│   ├── __init__.py
│   └── db.py           # SQLite connection helper & row factory
├── routes/
│   ├── auth.py         # Login / Register / Logout
│   ├── dashboard.py    # Dashboard
│   ├── subjects.py     # Subjects CRUD
│   ├── schedule.py     # Study schedule CRUD
│   ├── tasks.py        # Tasks CRUD
│   ├── reminders.py    # Reminders CRUD
│   ├── progress.py     # Progress analytics
│   ├── reports.py      # Reports & charts
│   └── profile.py      # User profile
├── templates/          # Jinja2 HTML templates
└── static/             # CSS, JS, images
```

---

## Installation & Setup

### 1. Prerequisites

- Python 3.9+
- pip

*(Note: SQLite is included standard with Python, so no separate database server or MySQL installation is required!)*

### 2. Clone / Download

```bash
cd "Study Planner"
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize SQLite Database & Seed Demo Data

Run the initialization script to automatically create `database/study_planner.db` and insert sample data:

```bash
python database/init_db.py
```

### 5. Configure Environment Variables (Optional)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

The default values work out-of-the-box:

```
SECRET_KEY=a7fb9412d420cb1109225b23192d3c3686a7f1de442c45249f8b58af34fca635
DB_PATH=database/study_planner.db
```

### 6. Run the Application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:8080**

---

## Demo Credentials

| Field | Value |
|-------|-------|
| **Name** | Pranali Kharat |
| **Email** | pranali@example.com |
| **Password** | Demo@123 |
| **Course** | B.Sc. Computer Science |
| **Year** | TY B.Sc. |

The demo account has pre-loaded data including 5 subjects, 12 study sessions, 10 tasks, and 5 reminders.

---

## Security

- Passwords hashed with **bcrypt** (never stored in plain text)
- Session-based authentication with Flask sessions
- All routes protected with `login_required` decorator
- All SQL queries use parameterized statements (no SQL injection)
- User-level data isolation – users can only access their own data
- Configuration via `.env` file (never hardcoded)

---

## Known Limitations

- No email-based password reset (would require SMTP setup)
- No real-time push notifications (reminders are shown in-app only)
- No file upload for assignments

---

## License

Academic project for TY B.Sc. Computer Science – Pune University.
