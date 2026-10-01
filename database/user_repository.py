"""User accounts (PBKDF2-hashed passwords)."""
import hashlib
import hmac
import secrets
import sqlite3

from database.db_connection import db_session, query, query_one
from utils.constants import ROLE_STUDENT, ROLES
from utils.helpers import now_iso

_ITERATIONS = 120_000
_PUBLIC = "user_id, name, email, role, credits, created_at"


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), _ITERATIONS)
    return digest.hex(), salt


def create_user(name: str, email: str, password: str, role: str = ROLE_STUDENT) -> int:
    if role not in ROLES:
        raise ValueError("Invalid role.")
    pw_hash, salt = hash_password(password)
    try:
        with db_session() as conn:
            cur = conn.execute(
                "INSERT INTO users(name,email,password_hash,salt,role,credits,created_at) "
                "VALUES(?,?,?,?,?,0,?)",
                (name.strip(), email.strip().lower(), pw_hash, salt, role, now_iso()),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("An account with this email already exists.")


def authenticate(email: str, password: str):
    row = query_one("SELECT * FROM users WHERE email = ?", ((email or "").strip().lower(),))
    if not row:
        return None
    candidate, _ = hash_password(password or "", row["salt"])
    if hmac.compare_digest(candidate, row["password_hash"]):
        return get_user(row["user_id"])
    return None


def get_user(user_id: int):
    return query_one(f"SELECT {_PUBLIC} FROM users WHERE user_id = ?", (user_id,))


def get_user_by_email(email: str):
    return query_one(f"SELECT {_PUBLIC} FROM users WHERE email = ?", (email.strip().lower(),))


def list_users(role: str | None = None) -> list[dict]:
    if role:
        return query(f"SELECT {_PUBLIC} FROM users WHERE role = ? ORDER BY name", (role,))
    return query(f"SELECT {_PUBLIC} FROM users ORDER BY role, name")


def count_users() -> int:
    return query_one("SELECT COUNT(*) AS n FROM users")["n"]

def leaderboard(limit: int = 10) -> list[dict]:
    """Return the top student users ordered by credits."""

    if limit <= 0:
        raise ValueError("Leaderboard limit must be greater than 0.")

    return query(
        "SELECT user_id, name, credits FROM users WHERE role='student' "
        "ORDER BY credits DESC, name LIMIT ?", (limit,))


def rank_of(user_id: int):
    rows = query("SELECT user_id FROM users WHERE role='student' ORDER BY credits DESC, name")
    for i, r in enumerate(rows, 1):
        if r["user_id"] == user_id:
            return i
    return None
