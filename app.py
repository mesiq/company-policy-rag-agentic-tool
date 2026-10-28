from flask import Flask, request, jsonify, session, render_template
from datetime import timedelta, date
import os
import secrets

from database import (
    initialize_database,
    get_connection,
    verify_login,
    get_employee,
    get_leave_balances
)


# ------------------------------------------
# 1. CREATE FLASK APPLICATION
# ------------------------------------------

app = Flask(__name__)

# Temporary local secret if environment variable is not set.
# Set FLASK_SECRET_KEY before production deployment.
app.secret_key = (
    os.environ.get("FLASK_SECRET_KEY")
    or secrets.token_hex(32)
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Local HTTP only
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2)
)


# ------------------------------------------
# 2. INITIALIZE SQLITE DATABASE
# ------------------------------------------

initialize_database()


# ------------------------------------------
# 3. HOME ROUTE
# ------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

#@app.route("/", methods=["GET"])
#def home():
#    return jsonify({
#        "application": "Employee Agentic RAG Chatbot",
##        "backend": "Flask",
 #       "database": "SQLite",
 #       "status": "Running",
 #       "message": "Employee API is ready"
 #   }), 200


# ------------------------------------------
# 4. HEALTH CHECK API
# ------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():

    with get_connection() as conn:
        conn.execute("SELECT 1").fetchone()

    return jsonify({
        "status": "success",
        "message": "Flask and SQLite are working"
    }), 200


# ------------------------------------------
# 5. EMPLOYEE LOGIN API
# ------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please send valid JSON data"
        }), 400

    employee_id = data.get("employee_id")
    password = data.get("password")

    if not isinstance(employee_id, str) or not isinstance(password, str):
        return jsonify({
            "error": "Employee ID and password are required"
        }), 400

    employee_id = employee_id.strip().upper()

    if not employee_id or not password:
        return jsonify({
            "error": "Employee ID and password cannot be empty"
        }), 400

    # Verify password against SQLite
    employee = verify_login(employee_id, password)

    if employee is None:
        return jsonify({
            "error": "Invalid employee ID or password"
        }), 401

    # Create employee session
    session.clear()
    session.permanent = True
    session["employee_id"] = employee["employee_id"]

    return jsonify({
        "message": "Login successful",
        "employee": employee
    }), 200


# ------------------------------------------
# 6. FETCH LOGGED-IN EMPLOYEE PROFILE
# ------------------------------------------

@app.route("/api/me", methods=["GET"])
def my_profile():

    employee_id = session.get("employee_id")

    if not employee_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    employee = get_employee(employee_id)

    if employee is None:
        session.clear()
        return jsonify({
            "error": "Employee not found or inactive"
        }), 401

    return jsonify({
        "message": "Employee profile retrieved",
        "employee": employee
    }), 200


# ------------------------------------------
# 7. FETCH LEAVE BALANCE
# ------------------------------------------

@app.route("/api/leave-balance", methods=["GET"])
def leave_balance():

    employee_id = session.get("employee_id")

    if not employee_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    # Confirm that the employee is still active
    employee = get_employee(employee_id)

    if employee is None:
        session.clear()
        return jsonify({
            "error": "Employee not found or inactive"
        }), 401

    year_text = request.args.get("year")

    if year_text is None:
        year = date.today().year
    elif len(year_text) == 4 and year_text.isdigit():
        year = int(year_text)
    else:
        return jsonify({
            "error": "Year must be a four-digit number"
        }), 400

    balances = get_leave_balances(employee_id, year)

    return jsonify({
        "employee_id": employee_id,
        "year": year,
        "leave_balances": balances
    }), 200


# ------------------------------------------
# 8. EMPLOYEE LOGOUT
# ------------------------------------------

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    }), 200


# ------------------------------------------
# 9. START FLASK SERVER
# ------------------------------------------

if __name__ == "__main__":

    print("\nEmployee Agentic RAG Backend")
    print("Database connected successfully")
    print("Server starting at http://127.0.0.1:5000\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
