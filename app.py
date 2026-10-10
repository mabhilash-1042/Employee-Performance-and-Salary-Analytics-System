from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3
import csv
import io
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "employees.db")
app = Flask(__name__)
app.secret_key = "change-this-secret-key"


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                role TEXT NOT NULL,
                salary REAL NOT NULL CHECK (salary >= 0),
                performance REAL NOT NULL CHECK (performance >= 0 AND performance <= 100),
                productivity REAL NOT NULL CHECK (productivity >= 0 AND productivity <= 100),
                review_date TEXT NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        if count == 0:
            sample = [
                ("EMP001", "Aarav Sharma", "Engineering", "Software Engineer", 720000, 91, 88, "2026-09-15"),
                ("EMP002", "Priya Nair", "HR", "HR Executive", 480000, 84, 82, "2026-09-18"),
                ("EMP003", "Rohan Verma", "Sales", "Sales Analyst", 540000, 78, 91, "2026-09-20"),
                ("EMP004", "Ananya Rao", "Engineering", "Data Analyst", 810000, 96, 93, "2026-09-22"),
                ("EMP005", "Kabir Singh", "Finance", "Accountant", 600000, 73, 75, "2026-09-25"),
                ("EMP006", "Meera Iyer", "Marketing", "Marketing Specialist", 510000, 87, 89, "2026-09-26"),
                ("EMP007", "Ishaan Gupta", "Engineering", "QA Engineer", 660000, 82, 85, "2026-09-27"),
                ("EMP008", "Sana Khan", "Sales", "Sales Executive", 450000, 69, 78, "2026-09-29"),
            ]
            conn.executemany("""
                INSERT INTO employees
                (employee_code, name, department, role, salary, performance, productivity, review_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample)


def read_employee_form(form):
    employee = {
        "employee_code": form.get("employee_code", "").strip(),
        "name": form.get("name", "").strip(),
        "department": form.get("department", "").strip(),
        "role": form.get("role", "").strip(),
        "salary": form.get("salary", "").strip(),
        "performance": form.get("performance", "").strip(),
        "productivity": form.get("productivity", "").strip(),
        "review_date": form.get("review_date", "").strip(),
    }
    if not all(employee.values()):
        raise ValueError("Please fill in every field.")
    try:
        employee["salary"] = float(employee["salary"])
        employee["performance"] = float(employee["performance"])
        employee["productivity"] = float(employee["productivity"])
    except ValueError:
        raise ValueError("Salary, performance, and productivity must be numbers.")
    if employee["salary"] < 0:
        raise ValueError("Salary cannot be negative.")
    if not 0 <= employee["performance"] <= 100 or not 0 <= employee["productivity"] <= 100:
        raise ValueError("Performance and productivity must be between 0 and 100.")
    return employee


@app.route("/")
def dashboard():
    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()
    with get_db() as conn:
        departments = [r["department"] for r in conn.execute(
            "SELECT DISTINCT department FROM employees ORDER BY department"
        ).fetchall()]
        query = "SELECT * FROM employees WHERE (name LIKE ? OR employee_code LIKE ? OR role LIKE ?)"
        params = [f"%{search}%", f"%{search}%", f"%{search}%"]
        if department:
            query += " AND department = ?"
            params.append(department)
        query += " ORDER BY performance DESC, name"
        employees = conn.execute(query, params).fetchall()
        stats = conn.execute("""
            SELECT COUNT(*) AS total,
                   COALESCE(AVG(performance), 0) AS avg_performance,
                   COALESCE(AVG(salary), 0) AS avg_salary,
                   COALESCE(SUM(salary), 0) AS total_payroll,
                   SUM(CASE WHEN performance >= 85 THEN 1 ELSE 0 END) AS high_performers
            FROM employees
        """).fetchone()
        dept_rows = conn.execute("""
            SELECT department, AVG(performance) AS avg_performance,
                   AVG(salary) AS avg_salary, COUNT(*) AS headcount
            FROM employees GROUP BY department ORDER BY department
        """).fetchall()
    chart_data = {
        "names": [e["name"] for e in employees],
        "performance": [e["performance"] for e in employees],
        "salary": [e["salary"] for e in employees],
        "departments": [r["department"] for r in dept_rows],
        "departmentSalary": [round(r["avg_salary"], 2) for r in dept_rows],
        "departmentPerformance": [round(r["avg_performance"], 2) for r in dept_rows],
    }
    return render_template("dashboard.html", employees=employees, stats=stats,
                           departments=departments, selected_department=department,
                           search=search, chart_data=chart_data, dept_rows=dept_rows)


@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        try:
            e = read_employee_form(request.form)
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO employees
                    (employee_code, name, department, role, salary, performance, productivity, review_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, tuple(e[k] for k in ("employee_code", "name", "department", "role", "salary", "performance", "productivity", "review_date")))
            flash("Employee added successfully.", "success")
            return redirect(url_for("dashboard"))
        except ValueError as ex:
            flash(str(ex), "error")
        except sqlite3.IntegrityError:
            flash("Employee code already exists. Please use a unique code.", "error")
    return render_template("employee_form.html", employee=None, page_title="Add Employee")


@app.route("/employees/<int:employee_id>/edit", methods=["GET", "POST"])
def edit_employee(employee_id):
    with get_db() as conn:
        current = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    if current is None:
        flash("Employee not found.", "error")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        try:
            e = read_employee_form(request.form)
            with get_db() as conn:
                conn.execute("""
                    UPDATE employees SET employee_code=?, name=?, department=?, role=?,
                    salary=?, performance=?, productivity=?, review_date=? WHERE id=?
                """, tuple(e[k] for k in ("employee_code", "name", "department", "role", "salary", "performance", "productivity", "review_date")) + (employee_id,))
            flash("Employee details updated.", "success")
            return redirect(url_for("dashboard"))
        except ValueError as ex:
            flash(str(ex), "error")
        except sqlite3.IntegrityError:
            flash("Employee code already exists. Please use a unique code.", "error")
    return render_template("employee_form.html", employee=current, page_title="Edit Employee")


@app.route("/employees/<int:employee_id>/delete", methods=["POST"])
def delete_employee(employee_id):
    with get_db() as conn:
        conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    flash("Employee deleted.", "success")
    return redirect(url_for("dashboard"))


@app.route("/export.csv")
def export_csv():
    with get_db() as conn:
        rows = conn.execute("SELECT employee_code, name, department, role, salary, performance, productivity, review_date FROM employees ORDER BY name").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Employee Code", "Name", "Department", "Role", "Annual Salary (INR)", "Performance Score", "Productivity Score", "Review Date"])
    for row in rows:
        writer.writerow(list(row))
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=employee_analytics.csv"})


@app.route("/health")
def health():
    return {"status": "ok"}


init_db()

if __name__ == "__main__":
    app.run(debug=True)
