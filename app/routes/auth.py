from flask import Blueprint, request, jsonify

from app.db import get_connection
from app.utils import verify_password, create_session, invalidate

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/api/login")
def login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, username, password_hash, full_name, role FROM users WHERE username = %s",
                    (username,),
                )
                user = cur.fetchone()
        finally:
            conn.close()
    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500

    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid username or password"}), 401

    token = create_session(user["username"])
    return jsonify({
        "token": token,
        "username": user["username"],
        "fullName": user["full_name"],
        "role": user["role"],
    }), 200


@auth_bp.post("/api/logout")
def logout():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:] if auth_header.startswith("Bearer ") else None
    invalidate(token)
    return jsonify({"message": "Logged out"}), 200
