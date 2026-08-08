from functools import wraps

from flask import request, jsonify, g

from app.utils import username_for


def require_auth(fn):
    """Decorator: rejects with 401 unless a valid Bearer token is present."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header[7:] if auth_header.startswith("Bearer ") else None
        username = username_for(token)
        if not username:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        g.username = username
        g.token = token
        return fn(*args, **kwargs)
    return wrapper
