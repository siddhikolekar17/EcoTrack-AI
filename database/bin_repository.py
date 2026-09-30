"""Smart bin registry and sensor readings."""
from datetime import datetime, timedelta

from database.db_connection import db_session, execute, query, query_one
from utils.helpers import bin_status, now_iso


def list_bins() -> list[dict]:
    return query("SELECT * FROM smart_bins ORDER BY bin_id")


def get_bin(bin_id: str):
    return query_one("SELECT * FROM smart_bins WHERE bin_id = ?", (bin_id,))


def add_bin(bin_id, location, category, capacity_l, lat, lon, fill_level=0.0) -> str:
    ts = now_iso()
    with db_session() as conn:
        conn.execute(
            "INSERT INTO smart_bins(bin_id,location,category,capacity_l,fill_level,status,lat,lon,updated_at) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (bin_id, location, category, capacity_l, fill_level, bin_status(fill_level), lat, lon, ts))
        conn.execute("INSERT INTO bin_readings(bin_id,fill_level,recorded_at) VALUES(?,?,?)",
                     (bin_id, fill_level, ts))
    return bin_id


def update_fill(bin_id: str, fill: float, recorded_at: str | None = None) -> None:
    ts = recorded_at or now_iso()
    with db_session() as conn:
        conn.execute("UPDATE smart_bins SET fill_level=?, status=?, updated_at=? WHERE bin_id=?",
                     (fill, bin_status(fill), ts, bin_id))
        conn.execute("INSERT INTO bin_readings(bin_id,fill_level,recorded_at) VALUES(?,?,?)",
                     (bin_id, fill, ts))


def add_reading_only(bin_id: str, fill: float, recorded_at: str) -> None:
    execute("INSERT INTO bin_readings(bin_id,fill_level,recorded_at) VALUES(?,?,?)",
            (bin_id, fill, recorded_at))


def get_readings(bin_id: str, hours: int = 48) -> list[dict]:
    since = (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")
    return query("SELECT fill_level, recorded_at FROM bin_readings WHERE bin_id=? AND recorded_at>=? "
                 "ORDER BY recorded_at, reading_id", (bin_id, since))
