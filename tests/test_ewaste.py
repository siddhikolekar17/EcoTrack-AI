import pytest

from database import ewaste_repository, user_repository
from modules import ewaste_manager, qr_generator


def _users(db):
    s = user_repository.create_user("Stu", "s@x.io", "secret1", "student")
    a = user_repository.create_user("Adm", "a@x.io", "secret1", "admin")
    return s, a


def test_full_lifecycle_and_credits(db):
    s, a = _users(db)
    asset = ewaste_manager.register_asset(s, "Old laptop", "Laptop / Desktop", "CS Lab", "Damaged", 1)
    aid = asset["asset_id"]
    assert asset["status"] == "QR Generated" and asset["qr_path"]
    ewaste_manager.advance(aid, a)                       # Collected
    ewaste_manager.advance(aid, a)                       # Verified (+25)
    with pytest.raises(ValueError):                      # handover needs recycler
        ewaste_manager.advance(aid, a)
    ewaste_manager.advance(aid, a, recycler="GreenCycle", destination="Pune")
    with pytest.raises(ValueError):                      # certificate required
        ewaste_manager.advance(aid, a)
    done = ewaste_manager.advance(aid, a, certificate="CERT-1")   # +15
    assert done["status"] == "Recycling Completed"
    assert user_repository.get_user(s)["credits"] == 40
    with pytest.raises(ValueError):
        ewaste_manager.advance(aid, a)
    assert len(ewaste_repository.list_logs(asset_id=aid)) == 6


def test_students_cannot_advance(db):
    s, _ = _users(db)
    asset = ewaste_manager.register_asset(s, "Battery", "Lithium Battery", "Lab", "Damaged", 2)
    with pytest.raises(ValueError):
        ewaste_manager.advance(asset["asset_id"], s)


def test_qr_payload_roundtrip():
    payload = qr_generator.build_payload("ECO-EW-1", "x", "y")
    assert qr_generator.extract_asset_id(payload) == "ECO-EW-1"
    assert qr_generator.extract_asset_id("ECO-EW-2") == "ECO-EW-2"
