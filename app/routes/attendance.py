from datetime import date

from flask import Blueprint, request, jsonify
import pymysql

from app.db import get_connection
from app.auth_decorator import require_auth

attendance_bp = Blueprint("attendance", __name__)


def _fmt_time(t):
    if t is None:
        return None
    if hasattr(t, "strftime"):
        return t.strftime("%H:%M")
    # PyMySQL returns TIME columns as datetime.timedelta, not datetime.time
    total_seconds = int(t.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}"


def _row_to_dict(row):
    return {
        "id": row["id"],
        "employeeId": row["employee_id"],
        "employeeName": f'{row["first_name"]} {row["last_name"]}',
        "employeeCode": row["employee_code"],
        "date": row["date"].isoformat() if row["date"] else None,
        "status": row["status"],
        "checkIn": _fmt_time(row.get("check_in")),
        "checkOut": _fmt_time(row.get("check_out")),
        "remarks": row["remarks"],
    }


@attendance_bp.get("/api/attendance")
@require_auth
def list_attendance():
    date_param = request.args.get("date", "").strip()
    employee_id = request.args.get("employeeId", "").strip()
    date_from = request.args.get("from", "").strip()
    date_to = request.args.get("to", "").strip()

    sql = """SELECT a.*, e.first_name, e.last_name, e.employee_code
              FROM attendance a JOIN employees e ON a.employee_id = e.id WHERE 1=1"""
    params = []

    if date_param:
        sql += " AND a.date = %s"
        params.append(date_param)
    if employee_id:
        sql += " AND a.employee_id = %s"
        params.append(int(employee_id))
    if date_from:
        sql += " AND a.date >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND a.date <= %s"
        params.append(date_to)

    sql += " ORDER BY a.date DESC, e.first_name ASC"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    return jsonify([_row_to_dict(r) for r in rows]), 200


@attendance_bp.post("/api/attendance")
@require_auth
def mark_attendance():
    body = request.get_json(silent=True) or {}
    employee_id = body.get("employeeId")
    att_date = body.get("date")
    status = body.get("status")

    if employee_id is None or not att_date or not status:
        return jsonify({"error": "employeeId, date and status are required"}), 400

    check_in = body.get("checkIn") or None
    check_out = body.get("checkOut") or None
    remarks = body.get("remarks")

    sql = """INSERT INTO attendance (employee_id, date, status, check_in, check_out, remarks)
             VALUES (%s,%s,%s,%s,%s,%s)
             ON DUPLICATE KEY UPDATE status=VALUES(status), check_in=VALUES(check_in),
                 check_out=VALUES(check_out), remarks=VALUES(remarks)"""
    params = (int(employee_id), att_date, status, check_in, check_out, remarks)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
    except pymysql.err.IntegrityError:
        return jsonify({"error": "Attendance already marked for this employee/date"}), 409
    finally:
        conn.close()

    return jsonify({"message": "Attendance saved"}), 200


@attendance_bp.put("/api/attendance/<int:att_id>")
@require_auth
def update_attendance(att_id):
    body = request.get_json(silent=True) or {}
    status = body.get("status")
    if not status:
        return jsonify({"error": "status is required"}), 400

    check_in = body.get("checkIn") or None
    check_out = body.get("checkOut") or None
    remarks = body.get("remarks")

    sql = "UPDATE attendance SET status=%s, check_in=%s, check_out=%s, remarks=%s WHERE id=%s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (status, check_in, check_out, remarks, att_id))
            updated = cur.rowcount
    finally:
        conn.close()

    if updated == 0:
        return jsonify({"error": "Attendance record not found"}), 404
    return jsonify({"message": "Attendance updated"}), 200


@attendance_bp.delete("/api/attendance/<int:att_id>")
@require_auth
def delete_attendance(att_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM attendance WHERE id = %s", (att_id,))
            deleted = cur.rowcount
    finally:
        conn.close()

    if deleted == 0:
        return jsonify({"error": "Attendance record not found"}), 404
    return jsonify({"message": "Attendance record deleted"}), 200


@attendance_bp.get("/api/attendance/summary")
@require_auth
def summary():
    today = date.today()
    month = request.args.get("month", str(today.month))
    year = request.args.get("year", str(today.year))
    employee_id = request.args.get("employeeId", "").strip()

    sql = """SELECT e.id, e.employee_code, e.first_name, e.last_name,
             SUM(CASE WHEN a.status='PRESENT' THEN 1 ELSE 0 END) AS present_count,
             SUM(CASE WHEN a.status='ABSENT' THEN 1 ELSE 0 END) AS absent_count,
             SUM(CASE WHEN a.status='HALF_DAY' THEN 1 ELSE 0 END) AS half_day_count,
             SUM(CASE WHEN a.status='LEAVE' THEN 1 ELSE 0 END) AS leave_count
             FROM employees e
             LEFT JOIN attendance a ON a.employee_id = e.id
                 AND MONTH(a.date) = %s AND YEAR(a.date) = %s
             WHERE 1=1"""
    params = [int(month), int(year)]

    if employee_id:
        sql += " AND e.id = %s"
        params.append(int(employee_id))

    sql += " GROUP BY e.id ORDER BY e.first_name"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    result = [{
        "employeeId": r["id"],
        "employeeCode": r["employee_code"],
        "employeeName": f'{r["first_name"]} {r["last_name"]}',
        "present": int(r["present_count"] or 0),
        "absent": int(r["absent_count"] or 0),
        "halfDay": int(r["half_day_count"] or 0),
        "leave": int(r["leave_count"] or 0),
    } for r in rows]

    return jsonify(result), 200
