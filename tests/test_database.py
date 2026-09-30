import pytest

from database import bin_repository, db_setup, user_repository


def test_create_and_authenticate(db):
    uid = user_repository.create_user("Test User", "T@Example.com", "secret1")
    assert user_repository.authenticate("t@example.com", "secret1")["user_id"] == uid
    assert user_repository.authenticate("t@example.com", "wrong") is None
    assert "password_hash" not in user_repository.get_user(uid)


def test_duplicate_email_rejected(db):
    user_repository.create_user("A", "a@x.io", "secret1")
    with pytest.raises(ValueError):
        user_repository.create_user("B", "a@x.io", "secret2")


def test_seed_creates_demo_data(db):
    db_setup.seed_demo_data()
    assert len(bin_repository.list_bins()) >= 3
    assert user_repository.leaderboard(3)
