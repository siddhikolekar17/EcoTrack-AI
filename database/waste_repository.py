"""Waste disposal records."""
from database.db_connection import db_session, execute, query, query_one
from utils.constants import WASTE_PENDING
from utils.helpers import now_iso


def add_record(user_id, category, item_label, confidence, weight_kg, image_path=None,
               model_name=None, created_at=None) -> int:
    return execute(
        "INSERT INTO waste_records(user_id,category,item_label,confidence,weight_kg,image_path,"
        "model_name,status,verified,created_at) VALUES(?,?,?,?,?,?,?,?,0,?)",
        (user_id, category, item_label, confidence, weight_kg, image_path, model_name,
         WASTE_PENDING, created_at or now_iso()))


def get_record(waste_id: int):
    return query_one("SELECT * FROM waste_records WHERE waste_id = ?", (waste_id,))


def list_records(status=None, user_id=None, limit=None) -> list[dict]:
    sql = ("SELECT w.*, u.name AS student FROM waste_records w "
           "JOIN users u ON u.user_id = w.user_id WHERE 1=1")
    params: list = []
    if status:
        sql += " AND w.status = ?"
        params.append(status)
    if user_id:
        sql += " AND w.user_id = ?"
        params.append(user_id)
    sql += " ORDER BY w.created_at DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(limit)
    return query(sql, tuple(params))


def set_status(waste_id, status, admin_id, note="", when=None):
    with db_session() as conn:
        conn.execute(
            "UPDATE waste_records SET status=?, verified=?, verified_by=?, verified_at=?, review_note=? "
            "WHERE waste_id=?",
            (status, 1 if status == "verified" else 0, admin_id, when or now_iso(), note, waste_id))


def count_verified(user_id: int) -> int:
    return query_one("SELECT COUNT(*) AS n FROM waste_records WHERE user_id=? AND status='verified'",
                     (user_id,))["n"]
