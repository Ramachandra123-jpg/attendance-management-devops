# 💼 Employee Management System

A web-based Employee Management System for managing employee records and
daily attendance.

**Stack:** Python (Flask) · MySQL · HTML / CSS / JavaScript

---

## 📖 Project Overview

The Employee Management System simplifies workforce management by allowing administrators to manage employee information, monitor attendance, and access organizational statistics from a single dashboard.

The application follows a modular Flask architecture with RESTful APIs and a responsive frontend for efficient employee administration.

---

## Features

- **Login** — token-based authentication with a seeded admin account
- **Employee management** — add, edit, delete, search and filter employees
  by name, code, email, department, or status
- **Attendance** — mark daily attendance per employee (Present / Absent /
  Half Day / Leave) with check-in/check-out times and remarks
- **Reports** — monthly attendance summary per employee
- **Dashboard** — live counts: total/active employees, present/absent/leave
  today, department count

---

## Project structure

```
ems/
├── requirements.txt          # Python dependencies (Flask, PyMySQL)
├── run.py                    # application entry point
├── app/
│   ├── __init__.py           # Flask app factory + static file serving
│   ├── config.py             # DB connection settings (env-var driven)
│   ├── db.py                 # database connection helper
│   ├── utils.py              # password hashing, session tokens
│   ├── auth_decorator.py     # @require_auth guard for protected routes
│   └── routes/
│       ├── auth.py           # /api/login, /api/logout
│       ├── employees.py      # /api/employees CRUD
│       ├── attendance.py     # /api/attendance CRUD + monthly summary
│       └── dashboard.py      # /api/dashboard/stats
├── database/
│   └── schema.sql            # MySQL schema + seed data
└── static/                   # front-end: HTML, CSS, JS (served as static files)
    ├── index.html            # login page
    ├── dashboard.html
    ├── employees.html
    ├── attendance.html
    ├── reports.html
    ├── css/style.css
    └── js/
```

---

## 1. Install prerequisites

- **Python 3.10+** — check with:
  ```bash
  python --version
  ```
  Get it from https://python.org if missing. On Windows, tick **"Add
  python.exe to PATH"** during install.

- **MySQL 8.x** — running locally or on a reachable server.

---

## 2. Set up the database

With MySQL running, load the schema:

```bash
mysql -u root -p < database/schema.sql
```

**Windows PowerShell** doesn't support the `<` redirect operator the same
way — use this instead:

```powershell
Get-Content database\schema.sql | mysql -u root -p
```

This creates the `ems_db` database and all tables, and seeds:
- an admin login → **username:** `admin` **password:** `admin123`
- a few sample departments and employees

---

## 3. Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

---

## 4. Configure the connection (optional)

Defaults live in `app/config.py` and can be overridden with environment
variables — no code changes needed:

| Variable      | Default     |
|---------------|-------------|
| `DB_HOST`     | `localhost` |
| `DB_PORT`     | `3306`      |
| `DB_NAME`     | `ems_db`    |
| `DB_USER`     | `root`      |
| `DB_PASSWORD` | `root`      |
| `SERVER_PORT` | `8080`      |

**macOS/Linux:**
```bash
export DB_PASSWORD="your_actual_password"
```

**Windows PowerShell:**
```powershell
$env:DB_PASSWORD="your_actual_password"
```

---

## 5. Run

```bash
python run.py
```

You should see:
```
[OK] Connected to MySQL database 'ems_db'
[OK] Server started at http://localhost:8080
     Default login -> username: admin  |  password: admin123
```

Open **http://localhost:8080** in a browser and log in with
`admin` / `admin123`.

---

## Running in VS Code

1. **File → Open Folder** → select the project folder (the one containing
   `run.py`).
2. Install the **Python extension** (by Microsoft) from the Extensions
   panel if you don't already have it.
3. Open the integrated terminal (`` Ctrl+` ``), set your DB password as
   shown above, then run `python run.py` — or click the **▷ Run** button
   at the top-right while `run.py` is open in the editor.

---

## Using the app

- **Dashboard** — quick stats (today's attendance, employee counts)
- **Employees** — add/edit/delete employee records, search and filter
- **Attendance** — pick a date, mark each active employee's status, save
- **Reports** — pick a month/year to see present/absent/half-day/leave
  totals per employee

> **Note on security:** password hashing here uses plain SHA-256, kept
> simple intentionally for a learning/demo project. For a real deployment,
> switch to a salted algorithm such as bcrypt or Argon2 (e.g. via the
> `passlib` or `bcrypt` package).
>
> Sessions are also stored **in-memory** in a single Python dictionary.
> This is fine for local use or a single-process deployment, but will
> break if you run multiple worker processes (e.g. `gunicorn -w 2`) since
> each process has its own separate session store. For production with
> multiple workers, move sessions into the database or a shared store like
> Redis.

---

## Deploying beyond localhost

Flask's built-in server (`app.run()`) is for development only. For real
traffic, run behind a production WSGI server:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:8080 "app:create_app()"
```

On Windows (gunicorn isn't supported), use `waitress` instead:

```powershell
pip install waitress
waitress-serve --port=8080 "app:create_app()"
```

For a public-facing site, put this behind a reverse proxy (e.g. Nginx),
add HTTPS (e.g. via Let's Encrypt/Certbot), and point a domain's DNS at
your server.

---

## REST API reference

All `/api/*` routes except `/api/login` require an
`Authorization: Bearer <token>` header (token returned by `/api/login`).

| Method | Endpoint                    | Description                                       |
|--------|------------------------------|----------------------------------------------------|
| POST   | `/api/login`                | Authenticate, returns a token                       |
| POST   | `/api/logout`               | Invalidate the current token                        |
| GET    | `/api/employees`            | List employees (`?search=&department=&status=`)     |
| GET    | `/api/employees/<id>`       | Get one employee                                    |
| POST   | `/api/employees`            | Create employee                                     |
| PUT    | `/api/employees/<id>`       | Update employee                                     |
| DELETE | `/api/employees/<id>`       | Delete employee                                     |
| GET    | `/api/attendance`           | List attendance (`?date=&employeeId=&from=&to=`)     |
| POST   | `/api/attendance`           | Mark/update attendance (upsert per employee+date)    |
| PUT    | `/api/attendance/<id>`      | Update an attendance record                          |
| DELETE | `/api/attendance/<id>`      | Delete an attendance record                          |
| GET    | `/api/attendance/summary`   | Monthly summary (`?month=&year=&employeeId=`)        |
| GET    | `/api/dashboard/stats`      | Dashboard counters                                   |

---

## Extending the project

- Add role-based permissions (the `users` table already has a `role` column)
- Add pagination to the employee/attendance lists for large datasets
- Export reports to CSV/PDF
- Add a "leave request" workflow with approval states
- Replace SHA-256 password hashing with bcrypt/Argon2 for production use

---

## 🎯 Learning Outcomes

- Flask Web Development
- REST API Development
- MySQL Database Design
- Authentication & Authorization
- CRUD Operations
- Full-Stack Web Development

---

## 👨‍💻 Author

**Parthan VA**

M.Tech Information Security

College of Engineering Trivandrum (CET)

- GitHub: https://github.com/parthan2001

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.