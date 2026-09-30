"""Analytics queries returning pandas DataFrames / summary dicts."""
from datetime import datetime, timedelta

import pandas as pd

from config import settings
from database import rewards_repository
from database.db_connection import get_connection
from utils.constants import CATEGORIES, EWASTE_LIFECYCLE


def _df(sql: str, params=()) -> pd.DataFrame:
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def _scalar(sql: str, params=()):
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchone()[0]
    finally:
        conn.close()


def summary() -> dict:
    by_cat = _df("SELECT category, SUM(weight_kg) AS kg FROM waste_records WHERE status='verified' "
                 "GROUP BY category")
    kg = {c: float(by_cat.loc[by_cat.category == c, "kg"].sum()) for c in CATEGORIES}
    return {
        "total_kg": sum(kg.values()),
        "kg_by_category": kg,
        "verified": _scalar("SELECT COUNT(*) FROM waste_records WHERE status='verified'"),
        "pending": _scalar("SELECT COUNT(*) FROM waste_records WHERE status='pending'"),
        "active_bins": _scalar("SELECT COUNT(*) FROM smart_bins"),
        "bins_need_collection": _scalar("SELECT COUNT(*) FROM smart_bins WHERE fill_level >= ?",
                                        (settings.BIN_WARNING,)),
        "overflow_bins": _scalar("SELECT COUNT(*) FROM smart_bins WHERE fill_level >= ?",
                                 (settings.BIN_OVERFLOW,)),
        "ewaste_assets": _scalar("SELECT COUNT(*) FROM ewaste_assets"),
        "credits_awarded": rewards_repository.total_awarded(),
        "impact_co2": round(sum(settings.IMPACT_FACTORS[c] * kg[c] for c in CATEGORIES), 1),
    }


def category_distribution() -> pd.DataFrame:
    return _df("SELECT category, ROUND(SUM(weight_kg),1) AS kg, COUNT(*) AS items FROM waste_records "
               "WHERE status='verified' GROUP BY category")


def daily_trend(days: int = 30) -> pd.DataFrame:
    since = (datetime.now() - timedelta(days=days)).isoformat(timespec="seconds")
    df = _df("SELECT date(created_at) AS day, category, SUM(weight_kg) AS kg FROM waste_records "
             "WHERE status='verified' AND created_at >= ? GROUP BY day, category ORDER BY day", (since,))
    return df


def ewaste_status() -> pd.DataFrame:
    df = _df("SELECT status, COUNT(*) AS assets, SUM(quantity) AS units FROM ewaste_assets GROUP BY status")
    order = {s: i for i, s in enumerate(EWASTE_LIFECYCLE)}
    return df.sort_values("status", key=lambda s: s.map(order)).reset_index(drop=True)


def participation() -> pd.DataFrame:
    return _df("SELECT u.name AS student, COUNT(w.waste_id) AS verified_disposals, "
               "ROUND(COALESCE(SUM(w.weight_kg),0),1) AS kg, u.credits "
               "FROM users u LEFT JOIN waste_records w ON w.user_id=u.user_id AND w.status='verified' "
               "WHERE u.role='student' GROUP BY u.user_id ORDER BY verified_disposals DESC, u.credits DESC")


def recent_activity(limit: int = 10) -> pd.DataFrame:
    return _df("SELECT w.created_at AS time, u.name AS student, w.category, w.item_label AS item, "
               "w.weight_kg AS kg, w.status FROM waste_records w JOIN users u ON u.user_id=w.user_id "
               "ORDER BY w.created_at DESC LIMIT ?", (limit,))


def all_waste_records() -> pd.DataFrame:
    return _df("SELECT w.waste_id, u.name AS student, w.category, w.item_label, w.confidence, w.weight_kg, "
               "w.status, w.created_at FROM waste_records w JOIN users u ON u.user_id=w.user_id "
               "ORDER BY w.created_at DESC")
