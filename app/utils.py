import hashlib
import secrets

# In-memory session store: token -> username.
# NOTE: resets on server restart, and won't work across multiple worker
# processes (fine for `flask run` / single-process `python run.py`; if you
# deploy behind gunicorn with >1 worker, move this to Redis or the DB).
_SESSIONS = {}


def hash_password(raw_password: str) -> str:
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, stored_hash: str) -> bool:
    return hash_password(raw_password) == (stored_hash or "").lower()


def create_session(username: str) -> str:
    token = secrets.token_urlsafe(32)
    _SESSIONS[token] = username
    return token


def username_for(token: str):
    if not token:
        return None
    return _SESSIONS.get(token)


def invalidate(token: str):
    _SESSIONS.pop(token, None)
