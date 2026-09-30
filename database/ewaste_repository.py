"""E-waste assets and collection / lifecycle logs."""
from database.db_connection import db_session, execute, query, query_one
from utils.helpers import now_iso

_UPDATABLE = {"recycler_name", "destination", "certificate_no", "handover_date", "qr_path", "notes"}


def create_asset(asset_id, item, item_type, department, item_condition, quantity, status,
                 qr_path, notes, registered_by, created_at=None) -> str:
    ts = created_at or now_iso()
    execute(
        "INSERT INTO ewaste_assets(asset_id,item,item_type,department,item_condition,quantity,status,"
        "qr_path,notes,registered_by,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        (asset_id, item, item_type, department, item_condition, quantity, status, qr_path, notes,
         registered_by, ts, ts))
    return asset_id


def get_asset(asset_id: str):
    return query_one("SELECT a.*, u.name AS registered_by_name FROM ewaste_assets a "
                     "LEFT JOIN users u ON u.user_id = a.registered_by WHERE a.asset_id = ?",
                     (asset_id.strip(),))


def list_assets(status=None, user_id=None) -> list[dict]:
    sql = ("SELECT a.*, u.name AS registered_by_name FROM ewaste_assets a "
           "LEFT JOIN users u ON u.user_id = a.registered_by WHERE 1=1")
    params: list = []
    if status:
        sql += " AND a.status = ?"
        params.append(status)
    if user_id:
        sql += " AND a.registered_by = ?"
        params.append(user_id)
    return query(sql + " ORDER BY a.created_at DESC", tuple(params))


def update_status(asset_id: str, status: str, **fields) -> None:
    bad = set(fields) - _UPDATABLE
    if bad:
        raise ValueError(f"Cannot update fields: {bad}")
    sets = ["status = ?", "updated_at = ?"] + [f"{k} = ?" for k in fields]
    params = [status, now_iso(), *fields.values(), asset_id]
    with db_session() as conn:
        conn.execute(f"UPDATE ewaste_assets SET {', '.join(sets)} WHERE asset_id = ?", params)


def add_log(action, asset_id=None, bin_id=None, destination=None, status=None, notes=None,
            performed_by=None, created_at=None) -> int:
    return execute(
        "INSERT INTO collection_logs(asset_id,bin_id,action,destination,status,notes,performed_by,created_at) "
        "VALUES(?,?,?,?,?,?,?,?)",
        (asset_id, bin_id, action, destination, status, notes, performed_by, created_at or now_iso()))


def list_logs(asset_id=None, bin_id=None, limit=200) -> list[dict]:
    sql = ("SELECT l.*, u.name AS performed_by_name FROM collection_logs l "
           "LEFT JOIN users u ON u.user_id = l.performed_by WHERE 1=1")
    params: list = []
    if asset_id:
        sql += " AND l.asset_id = ?"
        params.append(asset_id)
    if bin_id:
        sql += " AND l.bin_id = ?"
        params.append(bin_id)
    sql += " ORDER BY l.created_at DESC, l.collection_id DESC LIMIT ?"
    params.append(limit)
    return query(sql, tuple(params))


def counts_by_status() -> dict:
    return {r["status"]: r["n"] for r in
            query("SELECT status, COUNT(*) AS n FROM ewaste_assets GROUP BY status")}
