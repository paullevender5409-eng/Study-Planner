# Smart Study Planner

## 1. Project Overview

Build a complete web-based **Smart Study Planner** for TY B.Sc. Computer Science students.

The application should help students organize their subjects, study schedules, assignments, reminders, and academic progress from a single dashboard.

**Tagline:** Plan Smart. Study Better. Achieve More.

---

## 2. Tech Stack

* **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
* **Backend:** Python Flask
* **Database:** MySQL
* **Charts:** Chart.js
* **IDE:** VS Code

Do not use Node.js unless absolutely necessary.

---

## 3. Main Modules

### 1. Authentication

* Student registration
* Login/logout
* Password hashing
* Session-based authentication

### 2. Student Profile

* View/edit profile
* Name, email, college, course, year, phone
* Study goal and preferred study hours
* Change password

### 3. Subject Management

* Add, edit, delete subjects
* Subject name, code, teacher, semester
* Subject-wise activity tracking

### 4. Study Schedule

* Create study sessions
* Subject, topic, date, start/end time
* Study type: Reading, Revision, Practice, Exam Prep, Project
* Priority and notes
* Calendar/list view
* Mark session completed

### 5. Tasks & Reminders

* Create assignments, homework, projects, exams and presentations
* Due date/time
* Priority and status
* Edit/delete/complete tasks
* Search and filter
* Detect overdue tasks
* In-app reminders/notifications

### 6. Progress & Reports

Track:

* Completed/pending tasks
* Study hours
* Weekly/monthly study hours
* Subject-wise study time
* Task completion percentage
* Study streak

Provide charts for:

* Weekly study hours
* Subject-wise study hours
* Task completion
* Monthly activity

---

## 4. Dashboard

Create a modern dashboard containing:

* Welcome message
* Total subjects
* Today's study sessions
* Pending tasks
* Completed tasks
* Total study hours
* Today's schedule
* Upcoming deadlines
* Overdue tasks
* Progress percentage
* Study charts

All dashboard values must come from the database, not hardcoded values.

---

## 5. Database

Database name:

`smart_study_planner`

Tables:

```text
users
subjects
study_sessions
tasks
reminders
notifications
```

Use proper foreign keys and timestamps.

Every record must belong to the logged-in student.

**Important:** A student must never be able to view or modify another student's data.

---

## 6. UI/UX

Create a clean, modern student productivity interface.

Use:

* Sidebar navigation
* Responsive layout
* Cards
* Tables
* Forms
* Modals
* Toast notifications
* Progress bars
* Charts
* Calendar

Navigation:

```text
Dashboard
Subjects
Study Schedule
Tasks
Reminders
Progress
Reports
Profile
Logout
```

Use a professional blue/indigo academic theme.

The UI must be responsive for desktop and mobile.

---

## 7. Security

Implement:

* Password hashing
* Flask sessions
* Protected routes
* Input validation
* SQL injection protection
* `.env` for database credentials and secret key
* User-level data authorization

Never store plain-text passwords.

---

## 8. Project Structure

Use a clean Flask structure:

```text
smart-study-planner/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env.example
├── database/
│   └── schema.sql
├── models/
├── routes/
├── templates/
└── static/
    ├── css/
    ├── js/
    └── images/
```

---

## 9. Sample Data

Include demo data for:

* 5 subjects
* Several study sessions
* Tasks with different statuses
* Upcoming and overdue tasks
* Reminders

Use demo student:

```text
Name: Pranali Kharat
Email: pranali@example.com
Password: Demo@123
Course: B.Sc. Computer Science
Year: TY B.Sc.
```

---

## 10. Requirements

Generate:

* `requirements.txt`
* `schema.sql`
* `.env.example`
* `README.md`

README must explain installation, MySQL setup, environment configuration, running the application, and demo credentials.

---

## 11. Development Instructions

Build the **complete working application**, not just a UI prototype.

After implementation:

1. Run the application.
2. Test registration/login.
3. Test CRUD operations.
4. Test database persistence.
5. Test dashboard calculations.
6. Test charts and reports.
7. Test authorization.
8. Fix any errors found.

Keep the code simple and understandable because this is a **TY B.Sc. Computer Science college project**.

Start building the project from this PRD.
