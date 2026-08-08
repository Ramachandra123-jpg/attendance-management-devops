from flask import Blueprint, request, jsonify

import pymysql

from app.db import get_connection
from app.auth_decorator import require_auth

employees_bp = Blueprint("employees", __name__)

REQUIRED_FIELDS = ["employeeCode", "firstName", "lastName", "email"]


def _row_to_dict(row):
    return {
        "id": row["id"],
        "employeeCode": row["employee_code"],
        "firstName": row["first_name"],
        "lastName": row["last_name"],
        "email": row["email"],
        "phone": row["phone"],
        "department": row["department"],
        "designation": row["designation"],
        "dateOfJoining": row["date_of_joining"].isoformat() if row["date_of_joining"] else None,
        "salary": float(row["salary"]) if row["salary"] is not None else 0,
        "status": row["status"],
        "address": row["address"],
    }


def _missing_field(body):
    for f in REQUIRED_FIELDS:
        if not body.get(f):
            return f
    return None


@employees_bp.get("/api/employees")
@require_auth
def list_employees():
    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()

    sql = "SELECT * FROM employees WHERE 1=1"
    params = []

    if search:
        sql += " AND (first_name LIKE %s OR last_name LIKE %s OR employee_code LIKE %s OR email LIKE %s)"
        like = f"%{search}%"
        params += [like, like, like, like]
    if department:
        sql += " AND department = %s"
        params.append(department)
    if status:
        sql += " AND status = %s"
        params.append(status)

    sql += " ORDER BY id DESC"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify([_row_to_dict(r) for r in rows]), 200


@employees_bp.get("/api/employees/<int:emp_id>")
@require_auth
def get_employee(emp_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(_row_to_dict(row)), 200


@employees_bp.post("/api/employees")
@require_auth
def create_employee():
    body = request.get_json(silent=True) or {}
    missing = _missing_field(body)
    if missing:
        return jsonify({"error": f"Missing field: {missing}"}), 400

    sql = """INSERT INTO employees
             (employee_code, first_name, last_name, email, phone, department,
              designation, date_of_joining, salary, status, address)
             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    params = (
        body.get("employeeCode"), body.get("firstName"), body.get("lastName"),
        body.get("email"), body.get("phone"), body.get("department"),
        body.get("designation"), body.get("dateOfJoining") or None,
        body.get("salary") or 0, body.get("status") or "ACTIVE", body.get("address"),
    )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            new_id = cur.lastrowid
    except pymysql.err.IntegrityError as e:
        return jsonify({"error": f"Duplicate employee code or email: {e}"}), 409
    finally:
        conn.close()

    return jsonify({"id": new_id, "message": "Employee created"}), 201


@employees_bp.put("/api/employees/<int:emp_id>")
@require_auth
def update_employee(emp_id):
    body = request.get_json(silent=True) or {}
    missing = _missing_field(body)
    if missing:
        return jsonify({"error": f"Missing field: {missing}"}), 400

    sql = """UPDATE employees SET employee_code=%s, first_name=%s, last_name=%s, email=%s,
             phone=%s, department=%s, designation=%s, date_of_joining=%s, salary=%s,
             status=%s, address=%s WHERE id=%s"""
    params = (
        body.get("employeeCode"), body.get("firstName"), body.get("lastName"),
        body.get("email"), body.get("phone"), body.get("department"),
        body.get("designation"), body.get("dateOfJoining") or None,
        body.get("salary") or 0, body.get("status") or "ACTIVE", body.get("address"),
        emp_id,
    )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            updated = cur.rowcount
    except pymysql.err.IntegrityError as e:
        return jsonify({"error": f"Duplicate employee code or email: {e}"}), 409
    finally:
        conn.close()

    if updated == 0:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify({"message": "Employee updated"}), 200


@employees_bp.delete("/api/employees/<int:emp_id>")
@require_auth
def delete_employee(emp_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
            deleted = cur.rowcount
    finally:
        conn.close()

    if deleted == 0:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify({"message": "Employee deleted"}), 200
