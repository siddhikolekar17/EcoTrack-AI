"""In-app collection alerts (deduplicated, auto-resolved)."""
from database.db_connection import db_session, query
from modules import smart_bin
from utils.constants import BIN_NORMAL, BIN_OVERFLOW_STATUS, BIN_WARN
from utils.helpers import now_iso


def notify(level: str, title: str, message: str, ref: str) -> bool:
    """Create a notification unless an unread one with the same ref exists."""
    with db_session() as conn:
        dup = conn.execute("SELECT 1 FROM notifications WHERE ref=? AND is_read=0", (ref,)).fetchone()
        if dup:
            return False
        conn.execute("INSERT INTO notifications(level,title,message,ref,is_read,created_at) VALUES(?,?,?,?,0,?)",
                     (level, title, message, ref, now_iso()))
        return True


def unread() -> list[dict]:
    return query("SELECT * FROM notifications WHERE is_read=0 ORDER BY created_at DESC")


def list_all(limit: int = 100) -> list[dict]:
    return query("SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?", (limit,))


def mark_read(notification_id: int) -> None:
    with db_session() as conn:
        conn.execute("UPDATE notifications SET is_read=1 WHERE notification_id=?", (notification_id,))


def mark_all_read() -> None:
    with db_session() as conn:
        conn.execute("UPDATE notifications SET is_read=1")


def check_bins_and_alert() -> int:
    """Create alerts for overflow / warning / predicted-full bins; resolve alerts for emptied bins."""
    created = 0
    df = smart_bin.bins_dataframe()
    for _, r in df.iterrows():
        bid = r["bin_id"]
        if r["status"] == BIN_NORMAL:
            with db_session() as conn:  # auto-resolve alerts once the bin is fine again
                conn.execute("UPDATE notifications SET is_read=1 WHERE ref LIKE ? AND is_read=0", (f"%:{bid}",))
        if r["status"] == BIN_OVERFLOW_STATUS:
            created += notify("critical", f"Overflow: {bid}",
                              f"{bid} at {r['location']} is {r['fill_level']:.0f}% full - collect immediately.",
                              f"overflow:{bid}")
        elif r["status"] == BIN_WARN:
            created += notify("warning", f"Nearly full: {bid}",
                              f"{bid} at {r['location']} is {r['fill_level']:.0f}% full.", f"warning:{bid}")
        hrs = r["hours_to_full"]
        if hrs is not None and hrs == hrs and hrs < 6 and r["status"] != BIN_OVERFLOW_STATUS:
            created += notify("info", f"Predicted full soon: {bid}",
                              f"{bid} is forecast to be full in about {hrs:.1f} h.", f"predict:{bid}")
    return created
