# Employee AI Portal

A local employee self-service demo built with Flask, SQLite, and a single-page HTML frontend. It currently supports employee login, profile lookup, and leave-balance retrieval. The chat interface uses simple keyword matching; policy search and leave applications are placeholders, not implemented AI/RAG features.

## Features

- Employee login with password hashes stored in SQLite.
- Session-based authentication for employee profile and leave-balance endpoints.
- A dashboard with profile information, leave balances, and a chat-style interface.
- Demo data for 20 fictional employees across five departments.
- Database tables prepared for leave requests and HR tickets; workflows for these tables are not implemented yet.

## Requirements

- Python 3.9 or newer.
- `pip`.

## Setup on Windows

Open PowerShell in the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set both values. `DEMO_DEFAULT_PASSWORD` must match the password currently displayed on the login page (`Demo@12345`) for the seeded demo accounts to accept it:

```dotenv
DEMO_DEFAULT_PASSWORD=Demo@12345
FLASK_SECRET_KEY=choose-a-long-random-secret
```

The login page currently displays this shared demo password, so this setup is for local demonstration only. Do not use real employee data or reuse this password elsewhere. The `DEMO_DEFAULT_PASSWORD` value is used for all demo employees created during initial database seeding; changing it later does not update password hashes already stored in the database. The app reads `FLASK_SECRET_KEY` to sign session cookies. If it is omitted, the app generates a temporary key that changes when the app restarts, invalidating existing sessions. Do not commit `.env`.

Start the local development server:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. Sign in with the demo employee ID shown on the page. All seeded employees share the configured `DEMO_DEFAULT_PASSWORD`.

The SQLite database is created as `employee.db` beside the application files. The app creates its tables and seeds demo records when it starts, but only seeds when the employee table is empty. Deleting the local database and restarting the app recreates the demo data.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serves the employee portal. |
| `GET` | `/api/health` | Checks that the Flask app can query SQLite. |
| `POST` | `/api/login` | Accepts JSON with `employee_id` and `password`; establishes a session on success. |
| `GET` | `/api/me` | Returns the signed-in employee profile. |
| `GET` | `/api/leave-balance` | Returns leave balances for the signed-in employee. An optional `year` query parameter accepts four digits. |
| `POST` | `/api/logout` | Clears the current session. |

Example login request body:

```json
{
  "employee_id": "EMP1001",
  "password": "the DEMO_DEFAULT_PASSWORD value from your .env"
}
```

The browser uses the Flask session cookie when calling authenticated endpoints. API requests that require login return `401` when there is no valid session.

## Current limitations

- There is no language model, RAG knowledge base, policy document ingestion, or agent/tool orchestration.
- Chat actions are selected by client-side keyword matching and only profile and leave-balance queries call implemented backend features.
- Leave application and company-policy responses are placeholders.
- The HR-admin role is stored in employee data but is not used to authorize admin actions.
- The built-in Flask server runs in debug mode and is intended for local development only. Production deployment requires a production WSGI server, HTTPS, secure cookie settings, and production-grade secrets and data handling.

## Project files

- `app.py` — Flask application, page route, API endpoints, and session configuration.
- `database.py` — SQLite schema, demo seeding, authentication, employee lookup, and leave-balance functions.
- `templates/index.html` — Portal UI, styling, and browser-side API/chat logic.
- `requirements.txt` — Python package dependencies.
- `.env.example` — Environment-variable template; copy it to `.env` for local use.
