import pytest

from database import user_repository, waste_repository
from modules import green_credits, smart_bin


def test_verify_awards_points_once(db):
    s = user_repository.create_user("Stu", "s@x.io", "secret1")
    a = user_repository.create_user("Adm", "a@x.io", "secret1", "admin")
    wid = waste_repository.add_record(s, "Dry Recyclable", "bottle", 0.9, 0.4)
    assert green_credits.verify_submission(wid, a, True) == 10
    assert user_repository.get_user(s)["credits"] == 10
    with pytest.raises(ValueError):
        green_credits.verify_submission(wid, a, True)


def test_reject_awards_nothing(db):
    s = user_repository.create_user("Stu", "s@x.io", "secret1")
    a = user_repository.create_user("Adm", "a@x.io", "secret1", "admin")
    wid = waste_repository.add_record(s, "Biodegradable", "peel", 0.9, 0.2)
    assert green_credits.verify_submission(wid, a, False, "blurry") == 0
    assert user_repository.get_user(s)["credits"] == 0


def test_levels():
    assert green_credits.level_for(0)[0] == "Seedling"
    assert green_credits.level_for(60) == ("Eco Warrior", 150)


def test_bin_prediction_and_status():
    r = [{"fill_level": 20 + 5 * i, "recorded_at": f"2026-01-01T{i:02d}:00:00"} for i in range(6)]
    assert smart_bin.predict_hours_to_full(r) == pytest.approx(11.0, abs=0.2)
    assert smart_bin.status_for(95) == "Overflow Alert" and smart_bin.status_for(75) == "Warning"
    emptied = r + [{"fill_level": 0, "recorded_at": "2026-01-01T07:00:00"}]
    assert smart_bin.predict_hours_to_full(emptied) is None
