"""E-waste asset registration and lifecycle state machine."""
from config import settings
from database import ewaste_repository, rewards_repository, user_repository
from modules import qr_generator
from utils.constants import EWASTE_LIFECYCLE, ROLE_ADMIN, ROLE_STUDENT, STAFF_ROLES
from utils.helpers import generate_asset_id, now_iso

STAGE_REGISTERED, STAGE_QR, STAGE_COLLECTED, STAGE_VERIFIED, STAGE_HANDOVER, STAGE_DONE = EWASTE_LIFECYCLE


def register_asset(user_id: int, item: str, item_type: str, department: str, item_condition: str,
                   quantity: int, notes: str = "") -> dict:
    """Register an asset, generate its QR tag, and log the first two lifecycle stages."""
    asset_id = generate_asset_id()
    qr_path = qr_generator.generate_qr(asset_id, qr_generator.build_payload(asset_id, item, department))
    ewaste_repository.create_asset(asset_id, item, item_type, department, item_condition, quantity,
                                   STAGE_QR, qr_path, notes, user_id)
    ewaste_repository.add_log(STAGE_REGISTERED, asset_id=asset_id, status=STAGE_REGISTERED,
                              notes=f"{quantity} x {item} from {department}", performed_by=user_id)
    ewaste_repository.add_log(STAGE_QR, asset_id=asset_id, status=STAGE_QR,
                              notes="Unique QR asset tag generated", performed_by=user_id)
    return ewaste_repository.get_asset(asset_id)


def next_stage(status: str):
    i = EWASTE_LIFECYCLE.index(status)
    return EWASTE_LIFECYCLE[i + 1] if i + 1 < len(EWASTE_LIFECYCLE) else None


def advance(asset_id: str, performed_by: int, recycler: str = "", destination: str = "",
            certificate: str = "", notes: str = "") -> dict:
    """Move an asset to its next lifecycle stage, enforcing the audit rules."""
    asset = ewaste_repository.get_asset(asset_id)
    if not asset:
        raise ValueError("Asset not found.")
    actor = user_repository.get_user(performed_by)
    if not actor or actor["role"] not in STAFF_ROLES:
        raise ValueError("Only staff can advance the lifecycle.")
    nxt = next_stage(asset["status"])
    if nxt is None:
        raise ValueError("Lifecycle already completed.")

    fields = {}
    if nxt == STAGE_VERIFIED and asset["registered_by"] == performed_by and actor["role"] != ROLE_ADMIN:
        raise ValueError("Separation of duties: someone else must verify assets you registered.")
    if nxt == STAGE_HANDOVER:
        if not recycler.strip() or not destination.strip():
            raise ValueError("Recycler name and destination are required for handover.")
        fields = {"recycler_name": recycler.strip(), "destination": destination.strip(),
                  "handover_date": now_iso()}
    if nxt == STAGE_DONE:
        if not certificate.strip():
            raise ValueError("A recycling certificate number is required to close the record.")
        fields = {"certificate_no": certificate.strip()}

    ewaste_repository.update_status(asset_id, nxt, **fields)
    ewaste_repository.add_log(nxt, asset_id=asset_id, destination=fields.get("destination"), status=nxt,
                              notes=notes or fields.get("certificate_no"), performed_by=performed_by)

    owner = user_repository.get_user(asset["registered_by"]) if asset["registered_by"] else None
    if owner and owner["role"] == ROLE_STUDENT:
        if nxt == STAGE_VERIFIED:
            rewards_repository.add_reward(owner["user_id"], settings.CREDIT_RULES["ewaste_verified"],
                                          f"E-waste verified: {asset['item']}", "ewaste", asset_id)
        elif nxt == STAGE_DONE:
            rewards_repository.add_reward(owner["user_id"], settings.CREDIT_RULES["recycling_completed"],
                                          f"Recycling completed: {asset['item']}", "ewaste", asset_id)
    return ewaste_repository.get_asset(asset_id)
