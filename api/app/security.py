import hashlib
import os
import secrets
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

hasher = PasswordHasher()

_DUMMY_HASH = hasher.hash("dummy password")

SESSION_COOKIE = "session"
SESSION_TTL = timedelta(days=14)
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "1") == "1"

def hash_password(password: str) -> str:
    return hasher.hash(password)

def verify_password(password_hash: str | None, password: str) -> bool:
    try:
        return hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerifyMismatchError, InvalidHashError):
        return False

def new_session_token() -> str:
    return secrets.token_urlsafe(32)

def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()