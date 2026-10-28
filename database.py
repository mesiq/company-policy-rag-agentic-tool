
import sqlite3
import os
from pathlib import Path
from datetime import date
from contextlib import contextmanager

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


# 1. DATABASE LOCATION
DB_PATH = Path(__file__).resolve().parent / "employee.db"
load_dotenv(Path(__file__).resolve().parent / ".env")


def _get_demo_password():
    password = os.getenv("DEMO_DEFAULT_PASSWORD")
    if not password:
        raise RuntimeError(
            "DEMO_DEFAULT_PASSWORD must be set in the .env file or environment."
        )
    return password


# 2. DATABASE CONNECTION
@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# 3. CREATE DATABASE TABLES
def create_tables():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department_id INTEGER NOT NULL,
            designation TEXT NOT NULL,
            joining_date TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (department_id)
                REFERENCES departments(department_id)
        );

        CREATE TABLE IF NOT EXISTS credentials (
            employee_id TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee',
            FOREIGN KEY (employee_id)
                REFERENCES employees(employee_id)
        );

        CREATE TABLE IF NOT EXISTS leave_balances (
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            year INTEGER NOT NULL,
            total_days INTEGER NOT NULL,
            used_days INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (employee_id, leave_type, year),
            FOREIGN KEY (employee_id)
                REFERENCES employees(employee_id)
        );

        CREATE TABLE IF NOT EXISTS leave_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days_requested INTEGER NOT NULL,
            reason TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id)
                REFERENCES employees(employee_id)
        );

        CREATE TABLE IF NOT EXISTS hr_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id)
                REFERENCES employees(employee_id)
        );
        """)


# 4. INSERT SAMPLE EMPLOYEES
def seed_demo_data():
    with get_connection() as conn:

        # Do not recreate employees every time
        count = conn.execute(
            "SELECT COUNT(*) FROM employees"
        ).fetchone()[0]

        if count > 0:
            return

        demo_password = _get_demo_password()

        departments = [
            "IT", "HR", "Finance", "Sales", "Operations"
        ]

        for department in departments:
            conn.execute(
                "INSERT INTO departments (department_name) VALUES (?)",
                (department,)
            )

        dept_rows = conn.execute(
            "SELECT * FROM departments"
        ).fetchall()

        dept_ids = {
            row["department_name"]: row["department_id"]
            for row in dept_rows
        }

        employees = [
            ("EMP1001", "Aarav Sharma", "IT", "Developer"),
            ("EMP1002", "Priya Verma", "IT", "Data Analyst"),
            ("EMP1003", "Rohan Gupta", "IT", "AI Engineer"),
            ("EMP1004", "Sneha Rao", "IT", "Tester"),

            ("EMP1005", "Neha Singh", "HR", "HR Manager"),
            ("EMP1006", "Karan Mehta", "HR", "HR Executive"),
            ("EMP1007", "Pooja Nair", "HR", "Recruiter"),
            ("EMP1008", "Rahul Das", "HR", "HR Associate"),

            ("EMP1009", "Anjali Shah", "Finance", "Accountant"),
            ("EMP1010", "Vivek Kumar", "Finance", "Analyst"),
            ("EMP1011", "Ritika Jain", "Finance", "Finance Executive"),
            ("EMP1012", "Deepak Roy", "Finance", "Auditor"),

            ("EMP1013", "Aditya Patel", "Sales", "Sales Manager"),
            ("EMP1014", "Simran Kaur", "Sales", "Sales Executive"),
            ("EMP1015", "Nikhil Bose", "Sales", "Sales Associate"),
            ("EMP1016", "Meera Iyer", "Sales", "Account Manager"),

            ("EMP1017", "Sanjay Yadav", "Operations", "Team Lead"),
            ("EMP1018", "Kavya Menon", "Operations", "Coordinator"),
            ("EMP1019", "Arjun Reddy", "Operations", "Executive"),
            ("EMP1020", "Divya Kapoor", "Operations", "Analyst")
        ]

        for employee_id, name, department, designation in employees:

            email = name.lower().replace(" ", ".") + "@example.com"

            conn.execute("""
                INSERT INTO employees
                (employee_id, full_name, email,
                 department_id, designation, joining_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                employee_id,
                name,
                email,
                dept_ids[department],
                designation,
                "2024-01-15"
            ))

            # Every employee gets a hashed demo password
            password_hash = generate_password_hash(demo_password)

            role = (
                "hr_admin" if employee_id == "EMP1005"
                else "employee"
            )

            conn.execute("""
                INSERT INTO credentials
                (employee_id, password_hash, role)
                VALUES (?, ?, ?)
            """, (employee_id, password_hash, role))

            # Example leave balances
            leave_types = [
                ("Annual", 20, 4),
                ("Sick", 10, 2),
                ("Casual", 8, 1)
            ]

            for leave_type, total, used in leave_types:
                conn.execute("""
                    INSERT INTO leave_balances
                    (employee_id, leave_type, year,
                     total_days, used_days)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    employee_id,
                    leave_type,
                    date.today().year,
                    total,
                    used
                ))


# 5. FETCH EMPLOYEE DETAILS
def get_employee(employee_id):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                e.employee_id,
                e.full_name,
                e.email,
                d.department_name,
                e.designation,
                e.joining_date,
                c.role
            FROM employees e
            JOIN departments d
                ON e.department_id = d.department_id
            JOIN credentials c
                ON e.employee_id = c.employee_id
            WHERE e.employee_id = ?
              AND e.is_active = 1
        """, (employee_id,)).fetchone()

        return dict(row) if row else None


# 6. VERIFY EMPLOYEE LOGIN
def verify_login(employee_id, password):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT c.password_hash
            FROM credentials c
            JOIN employees e
                ON c.employee_id = e.employee_id
            WHERE c.employee_id = ?
              AND e.is_active = 1
        """, (employee_id,)).fetchone()

    if row and check_password_hash(row["password_hash"], password):
        return get_employee(employee_id)

    return None


# 7. CHECK EMPLOYEE LEAVE BALANCE
def get_leave_balances(employee_id, year=None):
    if year is None:
        year = date.today().year

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                leave_type,
                total_days,
                used_days,
                (total_days - used_days) AS remaining_days
            FROM leave_balances
            WHERE employee_id = ? AND year = ?
            ORDER BY leave_type
        """, (employee_id, year)).fetchall()

        return [dict(row) for row in rows]


# 8. INITIALIZE EVERYTHING
def initialize_database():
    create_tables()
    seed_demo_data()


# 9. RUN BASIC TESTS
if __name__ == "__main__":

    print("\n===== DATABASE INITIALIZATION =====")
    initialize_database()

    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM employees"
        ).fetchone()[0]

    print("Database:", DB_PATH.name)
    print("Total employees:", total)

    print("\n===== LOGIN TEST =====")

    user = verify_login("EMP1001", _get_demo_password())
    print("Valid login:", user is not None)

    invalid = verify_login("EMP1001", "WrongPassword")
    print("Invalid password rejected:", invalid is None)

    print("\n===== EMPLOYEE PROFILE =====")
    print(get_employee("EMP1001"))

    print("\n===== LEAVE BALANCE =====")
    for leave in get_leave_balances("EMP1001"):
        print(
            leave["leave_type"],
            "Remaining:",
            leave["remaining_days"]
        )

    print("\n===== ALL TESTS COMPLETED =====")
