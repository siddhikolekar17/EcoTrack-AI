"""Green credit rules, verification workflow and badges."""
from config import settings
from database import rewards_repository, waste_repository
from database.db_connection import query_one
from utils.constants import CREDIT_BADGES, WASTE_PENDING


def points_for(category: str) -> int:
    return settings.CREDIT_RULES.get(category, 0)


def verify_submission(waste_id: int, admin_id: int, approve: bool, note: str = "") -> int:
    """Approve/reject a pending submission. Returns credits awarded (0 if rejected)."""
    rec = waste_repository.get_record(waste_id)
    if not rec:
        raise ValueError("Submission not found.")
    if rec["status"] != WASTE_PENDING:
        raise ValueError("This submission has already been reviewed.")
    if not approve:
        waste_repository.set_status(waste_id, "rejected", admin_id, note)
        return 0
    waste_repository.set_status(waste_id, "verified", admin_id, note)
    pts = points_for(rec["category"])
    rewards_repository.add_reward(rec["user_id"], pts, f"Verified disposal: {rec['category']}",
                                  "waste", waste_id)
    return pts


def level_for(credits: int) -> tuple[str, int | None]:
    """Return (current level name, credits needed for next level or None)."""
    name, nxt = "Seedling", None
    for badge, need, _ in CREDIT_BADGES:
        if credits >= need:
            name = badge
        elif nxt is None:
            nxt = need
    return name, nxt


def badges_for(user_id: int, credits: int) -> list[str]:
    badges = [f"{icon} {name}" for name, need, icon in CREDIT_BADGES if credits >= need]
    if query_one("SELECT 1 AS x FROM rewards WHERE user_id=? AND ref_type='ewaste' LIMIT 1", (user_id,)):
        badges.append("💻 E-Waste Hero")
    if waste_repository.count_verified(user_id) >= 10:
        badges.append("🎯 Segregation Pro")
    return badges
