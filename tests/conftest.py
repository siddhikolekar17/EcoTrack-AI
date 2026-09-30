import pytest

from config import settings
from database import db_setup


@pytest.fixture()
def db(tmp_path, monkeypatch):
    """Fresh isolated database + output folders for each test."""
    monkeypatch.setattr(settings, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(settings, "QR_DIR", tmp_path / "qr")
    monkeypatch.setattr(settings, "UPLOAD_DIR", tmp_path / "uploads")
    db_setup.init_db()
    return tmp_path
