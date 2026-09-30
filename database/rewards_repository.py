"""Green credit ledger. Every credit change is a ledger row + balance update."""
from database.db_connection import db_session, query, query_one
from utils.helpers import now_iso


def add_reward(user_id, points, activity, ref_type=None, ref_id=None, created_at=None) -> None:
    with db_session() as conn:
        conn.execute(
            "INSERT INTO rewards(user_id,points,activity,ref_type,ref_id,created_at) VALUES(?,?,?,?,?,?)",
            (user_id, points, activity, ref_type, None if ref_id is None else str(ref_id),
             created_at or now_iso()))
        conn.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (points, user_id))


def list_rewards(user_id=None, limit=100) -> list[dict]:
    if user_id:
        return query("SELECT * FROM rewards WHERE user_id=? ORDER BY created_at DESC, reward_id DESC LIMIT ?",
                     (user_id, limit))
    return query("SELECT r.*, u.name AS student FROM rewards r JOIN users u USING(user_id) "
                 "ORDER BY r.created_at DESC, r.reward_id DESC LIMIT ?", (limit,))


def total_awarded() -> int:
    return query_one("SELECT COALESCE(SUM(points),0) AS n FROM rewards")["n"]
