from datetime import date

from flask import Blueprint, jsonify

from app.db import get_connection
from app.auth_decorator import require_auth

dashboard_bp = Blueprint("dashboard", __name__)


def _scalar(cur, sql, params=None):
    cur.execute(sql, params or ())
    row = cur.fetchone()
    return list(row.values())[0] if row else 0


@dashboard_bp.get("/api/dashboard/stats")
@require_auth
def stats():
    today = date.today().isoformat()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            data = {
                "totalEmployees": _scalar(cur, "SELECT COUNT(*) AS c FROM employees"),
                "activeEmployees": _scalar(cur, "SELECT COUNT(*) AS c FROM employees WHERE status='ACTIVE'"),
                "presentToday": _scalar(cur, "SELECT COUNT(*) AS c FROM attendance WHERE date=%s AND status='PRESENT'", (today,)),
                "absentToday": _scalar(cur, "SELECT COUNT(*) AS c FROM attendance WHERE date=%s AND status='ABSENT'", (today,)),
                "onLeaveToday": _scalar(cur, "SELECT COUNT(*) AS c FROM attendance WHERE date=%s AND status='LEAVE'", (today,)),
                "departments": _scalar(cur, "SELECT COUNT(DISTINCT department) AS c FROM employees"),
            }
    finally:
        conn.close()

    return jsonify(data), 200
